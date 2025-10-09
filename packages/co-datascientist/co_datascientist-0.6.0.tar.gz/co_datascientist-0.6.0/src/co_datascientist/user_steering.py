"""
User steering module for real-time direction input during workflow execution.
Provides non-blocking input capture to allow users to steer the evolution process.
"""

import asyncio
import sys
import threading
import os
import time
from typing import Optional
import logging


class SteeringAwareStdout:
    """Proxy for sys.stdout that buffers output while the user is typing steering input.

    When the steering handler is in input mode, writes are appended to a buffer.
    Otherwise, writes are forwarded to the underlying stdout immediately.
    """

    def __init__(self, steering_handler, underlying_stdout):
        self._handler = steering_handler
        self._underlying = underlying_stdout

    def write(self, s):
        try:
            if getattr(self._handler, 'input_mode_active', False):
                # Buffer during input mode
                with self._handler._lock:
                    self._handler.output_buffer.append(s)
            else:
                self._underlying.write(s)
                # After any normal write, redraw the status bar to keep it visible
                try:
                    if getattr(self._handler, 'status_bar_active', False) and not getattr(self._handler, 'input_mode_active', False):
                        self._handler._show_status_bar()
                except Exception:
                    pass
        except Exception:
            # In case of any error, fall back to direct write
            self._underlying.write(s)

    def flush(self):
        try:
            self._underlying.flush()
        except Exception:
            pass

    def isatty(self):
        try:
            return self._underlying.isatty()
        except Exception:
            return False

    def fileno(self):
        return getattr(self._underlying, 'fileno', lambda: -1)()

    def __getattr__(self, name):
        return getattr(self._underlying, name)


class UserSteeringHandler:
    """Handles non-blocking user input for steering the evolution process."""
    
    # ANSI color codes for styling
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    CLEAR_LINE = '\033[K'
    SAVE_CURSOR = '\033[s'
    RESTORE_CURSOR = '\033[u'
    MOVE_TO_BOTTOM = '\033[999;1H'
    
    def __init__(self):
        self.current_direction: Optional[str] = None
        self.direction_queue = asyncio.Queue()
        self.input_task: Optional[asyncio.Task] = None
        self.should_stop = False
        self._lock = threading.Lock()
        self.status_bar_active = False
        self.terminal_height = self._get_terminal_height()
        self.spinner_active = False
        self.spinner_text = ""
        self.spinner_frames = ['-', '\\', '|', '/']
        self.spinner_index = 0
        # Input-mode / buffering state
        self.input_mode_active = False
        self.output_buffer = []
        self._original_stdout = None
        self._stdout_proxy = None
        self._status_thread = None
        # Rendering suspension (for large output blocks)
        self._render_suspended = False

    def _direct_write(self, s: str):
        """Write directly to the original stdout to avoid proxy recursion."""
        try:
            if self._original_stdout is not None:
                self._original_stdout.write(s)
                self._original_stdout.flush()
            else:
                sys.__stdout__.write(s)
                sys.__stdout__.flush()
        except Exception:
            pass
    
    def _get_terminal_height(self) -> int:
        """Get terminal height, default to 24 if cannot determine."""
        try:
            return os.get_terminal_size().lines
        except:
            return 24
    
    def _show_status_bar(self):
        """Display the persistent status bar at the bottom."""
        if not self.status_bar_active or self._render_suspended or self.input_mode_active:
            return
            
        # Build status bar with steering state indicator and spinner status
        current_direction = self.get_current_direction()
        
        # Status with steering state (no spinner text)
        if current_direction:
            direction_preview = current_direction[:35] + ('...' if len(current_direction) > 35 else '')
            steering_text = f"{self.GREEN}STEERING{self.RESET} {self.BLUE}{direction_preview}{self.RESET}"
        else:
            steering_text = f"{self.GRAY}AUTOPILOT{self.RESET}"
        
        # Add spinner glyph if active (no text)
        if self.spinner_active:
            glyph = self.spinner_frames[self.spinner_index % len(self.spinner_frames)]
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_frames)
            status_line = f"{self.BLUE}{self.BOLD}> Type 'q' + Enter to steer{self.RESET} │ {steering_text} │ {self.YELLOW}{glyph}{self.RESET}"
        else:
            status_line = f"{self.BLUE}{self.BOLD}> Type 'q' + Enter to steer{self.RESET} │ {steering_text}"
        
        self._direct_write(f"{self.SAVE_CURSOR}{self.MOVE_TO_BOTTOM}{self.CLEAR_LINE}{status_line}{self.RESTORE_CURSOR}")
    
    def _clear_status_bar(self):
        """Clear the status bar."""
        self._direct_write(f"{self.SAVE_CURSOR}{self.MOVE_TO_BOTTOM}{self.CLEAR_LINE}{self.RESTORE_CURSOR}")

    async def start_listening(self):
        """Start the non-blocking input listener."""
        if self.input_task and not self.input_task.done():
            return  # Already listening
            
        self.should_stop = False
        self.status_bar_active = True
        # Install stdout proxy so we can buffer output during input mode
        if self._original_stdout is None:
            self._original_stdout = sys.stdout
        if self._stdout_proxy is None:
            self._stdout_proxy = SteeringAwareStdout(self, self._original_stdout)
        sys.stdout = self._stdout_proxy
        # Draw the status bar immediately so it's visible without waiting
        try:
            self._show_status_bar()
        except Exception:
            pass
        self.input_task = asyncio.create_task(self._input_loop())
        # Start the status bar display task
        self.status_task = asyncio.create_task(self._status_bar_loop())
        # Also start a background thread to keep bar visible during blocking ops
        try:
            if self._status_thread is None or not self._status_thread.is_alive():
                self._status_thread = threading.Thread(target=self._status_bar_thread_loop, daemon=True)
                self._status_thread.start()
        except Exception:
            pass
        logging.info("[STEERING] Started listening for user input")
    
    async def stop_listening(self):
        """Stop the input listener."""
        self.should_stop = True
        self.status_bar_active = False
        self._clear_status_bar()
        # Restore stdout
        try:
            if self._original_stdout is not None:
                sys.stdout = self._original_stdout
        except Exception:
            pass
        
        if self.input_task and not self.input_task.done():
            self.input_task.cancel()
            try:
                await self.input_task
            except asyncio.CancelledError:
                pass
                
        if hasattr(self, 'status_task') and not self.status_task.done():
            self.status_task.cancel()
            try:
                await self.status_task
            except asyncio.CancelledError:
                pass
        # Let the status thread exit on its own (daemon). No join needed.
                
        logging.info("[STEERING] Stopped listening for user input")
    
    async def _status_bar_loop(self):
        """Continuously update the status bar."""
        try:
            while not self.should_stop and self.status_bar_active:
                # Do not draw status bar while user is typing input
                if not self.input_mode_active and not self._render_suspended:
                    self._show_status_bar()
                await asyncio.sleep(0.5)  # Update every 500ms
        except asyncio.CancelledError:
            logging.info("[STEERING] Status bar loop cancelled")
            raise
        except Exception as e:
            logging.error(f"[STEERING] Status bar loop error: {e}")

    def _status_bar_thread_loop(self):
        """Background thread loop to keep bar pinned during blocking operations."""
        try:
            while not self.should_stop:
                if self.status_bar_active and not self.input_mode_active and not self._render_suspended:
                    self._show_status_bar()
                # Faster thread refresh so it competes with prints
                time.sleep(0.2)
        except Exception:
            pass

    # Public helpers for workflow code to hide the bar temporarily during large prints
    def suspend_bar(self):
        with self._lock:
            self._render_suspended = True
        # Clear immediately so it doesn't overwrite content
        try:
            self._clear_status_bar()
        except Exception:
            pass

    def resume_bar(self):
        with self._lock:
            self._render_suspended = False
        # Redraw immediately
        try:
            self._show_status_bar()
        except Exception:
            pass

    def _enter_input_mode(self):
        """Pause status bar and start buffering output."""
        with self._lock:
            self.input_mode_active = True
        # Clear status bar once when entering input mode
        self._clear_status_bar()

    def _exit_input_mode_and_flush(self):
        """Resume status bar and flush buffered output in order."""
        # Snapshot and clear buffer under lock
        with self._lock:
            buffered = self.output_buffer[:]
            self.output_buffer.clear()
            self.input_mode_active = False
        # Print buffered output without disturbing bottom bar
        if buffered:
            # Temporarily suspend drawing while flushing
            was_active = self.status_bar_active
            self.status_bar_active = False
            try:
                # Clear the bottom input line before replaying logs
                try:
                    self._clear_status_bar()
                except Exception:
                    pass
                # Restore cursor and print buffered content
                try:
                    if self._original_stdout is not None:
                        self._original_stdout.write(''.join(buffered))
                        self._original_stdout.flush()
                    else:
                        # Fallback
                        sys.__stdout__.write(''.join(buffered))
                        sys.__stdout__.flush()
                except Exception:
                    pass
            finally:
                self.status_bar_active = was_active

    async def _input_loop(self):
        """Main input listening loop."""
        try:
            while not self.should_stop:
                # Use run_in_executor to make input() non-blocking
                try:
                    user_input = await asyncio.get_event_loop().run_in_executor(
                        None, self._get_user_input
                    )
                    
                    if self.should_stop:
                        break
                        
                    if user_input is not None:
                        await self.direction_queue.put(user_input)
                        
                except Exception as e:
                    logging.warning(f"[STEERING] Input error: {e}")
                    await asyncio.sleep(1)  # Brief pause before retrying
                    
        except asyncio.CancelledError:
            logging.info("[STEERING] Input loop cancelled")
            raise
        except Exception as e:
            logging.error(f"[STEERING] Input loop error: {e}")
    
    def _wait_for_q_input(self) -> bool:
        """Wait for line input that starts with 'q' - no terminal raw mode manipulation."""
        try:
            # Simple approach: wait for a line of input and check if it starts with 'q'
            # This avoids all terminal mode manipulation that was causing formatting issues
            line = input().strip()
            return line.lower().startswith('q')
        except (EOFError, KeyboardInterrupt):
            return False
        except Exception as e:
            logging.warning(f"[STEERING] Error waiting for q input: {e}")
            return False
    
    def _get_user_input(self) -> Optional[str]:
        """Get user input synchronously (runs in thread executor)."""
        try:
            # Wait for input line starting with 'q' (no terminal mode manipulation)
            if not self._wait_for_q_input() or self.should_stop:
                return None
                
            # Enter input mode: pause bottom bar and start buffering all new output
            self._enter_input_mode()
            # Render a minimal inline prompt at bottom line and capture input
            try:
                prompt = f"{self.BLUE}{self.BOLD}Steering{self.RESET} > "
                self._direct_write(f"{self.SAVE_CURSOR}{self.MOVE_TO_BOTTOM}{self.CLEAR_LINE}{prompt}")
            except Exception:
                pass
            direction = input("").strip()
            
            if direction.lower() == 'clear':
                return ""  # Empty string means clear
            elif direction:
                result = direction
            else:
                result = None
                
            # Exit input mode and flush any buffered output
            self._exit_input_mode_and_flush()
            return result
        except (EOFError, KeyboardInterrupt):
            self._exit_input_mode_and_flush()
            return None
        except Exception as e:
            logging.warning(f"[STEERING] Error getting user input: {e}")
            self._exit_input_mode_and_flush()
            return None
    
    async def get_latest_direction(self) -> Optional[str]:
        """Get the most recent user direction if available."""
        try:
            # Get all pending directions, keep only the latest
            latest_direction = None
            while not self.direction_queue.empty():
                try:
                    latest_direction = await asyncio.wait_for(
                        self.direction_queue.get(), timeout=0.1
                    )
                except asyncio.TimeoutError:
                    break
            
            if latest_direction is not None:
                with self._lock:
                    if latest_direction == "":  # Clear signal
                        self.current_direction = None
                        logging.info("[STEERING] Direction cleared by user")
                    else:
                        self.current_direction = latest_direction
                        logging.info(f"[STEERING] New direction: {latest_direction}")
                
            return self.current_direction
            
        except Exception as e:
            logging.warning(f"[STEERING] Error getting direction: {e}")
            return self.current_direction
    
    def get_current_direction(self) -> Optional[str]:
        """Get the current direction synchronously."""
        with self._lock:
            return self.current_direction
    
    def set_spinner_status(self, active: bool, text: str = ""):
        """Update spinner status for integrated display."""
        with self._lock:
            self.spinner_active = active
            self.spinner_text = text
    
    def set_activity_status(self, status: str):
        """Set a general activity status (always show progress)."""
        with self._lock:
            self.spinner_active = True
            self.spinner_text = status


class CoordinatedSpinner:
    """Spinner wrapper that coordinates with the steering status bar."""
    
    def __init__(self, original_spinner, steering_handler: UserSteeringHandler):
        self.original_spinner = original_spinner
        self.steering_handler = steering_handler
        self._text = ""
        self._active = False
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        self._text = value
        if hasattr(self.original_spinner, 'text'):
            self.original_spinner.text = value
        # Update steering handler with spinner status (show text immediately)
        # Treat text updates as activity, even if not formally started.
        self.steering_handler.set_activity_status(value)
    
    def start(self):
        self._active = True
        if hasattr(self.original_spinner, 'start'):
            # If status bar isn't active yet, fall back to original spinner
            if not getattr(self.steering_handler, 'status_bar_active', False):
                self.original_spinner.start()
        # Activate spinner (glyph only) in the status bar
        self.steering_handler.set_spinner_status(True, self._text)
    
    def stop(self):
        self._active = False
        if hasattr(self.original_spinner, 'stop'):
            # Keep status bar spinner running as a heartbeat; only stop the original
            self.original_spinner.stop()
        # Do not disable the bar spinner; continue minimal activity
        # self.steering_handler.set_spinner_status(False, "")
    
    def write(self, message):
        """Write a message (pass through to original spinner)."""
        # Suspend bottom bar to avoid glyph remnants, then print, then resume
        try:
            self.steering_handler.suspend_bar()
        except Exception:
            pass
        try:
            if hasattr(self.original_spinner, 'write'):
                self.original_spinner.write(message)
            else:
                print(message)
        finally:
            try:
                self.steering_handler.resume_bar()
            except Exception:
                pass
    
    def __getattr__(self, name):
        """Delegate other attributes to original spinner."""
        return getattr(self.original_spinner, name)


# Global instance for the workflow runner
_steering_handler = None

def get_steering_handler() -> UserSteeringHandler:
    """Get the global steering handler instance."""
    global _steering_handler
    if _steering_handler is None:
        _steering_handler = UserSteeringHandler()
    return _steering_handler

def wrap_spinner_with_coordination(spinner):
    """Wrap a spinner to coordinate with the steering status bar."""
    if spinner is None:
        return None
    return CoordinatedSpinner(spinner, get_steering_handler())
