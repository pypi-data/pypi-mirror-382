#!/usr/bin/env python3
"""
Beautiful Python Diff PDF Generator - Simplified Version
Creates an aesthetic PDF diff with clean styling and intuitive color coding.
"""

import difflib
import argparse
import sys
import re
from pathlib import Path
from typing import List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import textwrap

class SimpleDiffPDFGenerator:
    def __init__(self):
        # Color scheme
        self.colors = {
            'added_bg': HexColor('#d4edda'),
            'added_border': HexColor('#28a745'),
            'removed_bg': HexColor('#f8d7da'),
            'removed_border': HexColor('#dc3545'),
            'unchanged_bg': white,
            'line_number_bg': HexColor('#f8f9fa'),
            'line_number_text': HexColor('#6c757d'),
            'header_bg': HexColor('#2d3ddb'),
        }
        
        # Styles
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=white,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # File info style
        self.styles.add(ParagraphStyle(
            name='FileInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=white,
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Stats style
        self.styles.add(ParagraphStyle(
            name='Stats',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=white,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Code style - unchanged
        self.styles.add(ParagraphStyle(
            name='CodeUnchanged',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName='Courier',
            leftIndent=0,
            rightIndent=0,
            spaceAfter=0,
            spaceBefore=0,
            leading=10,
            textColor=black
        ))
        
        # Code style - added
        self.styles.add(ParagraphStyle(
            name='CodeAdded',
            parent=self.styles['CodeUnchanged'],
            textColor=HexColor('#155724')
        ))
        
        # Code style - removed
        self.styles.add(ParagraphStyle(
            name='CodeRemoved',
            parent=self.styles['CodeUnchanged'],
            textColor=HexColor('#721c24')
        ))
        
        # Line number style
        self.styles.add(ParagraphStyle(
            name='LineNumber',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=self.colors['line_number_text'],
            alignment=TA_RIGHT,
            fontName='Courier-Bold',
            leading=10
        ))
    
    def escape_text(self, text: str) -> str:
        """Escape text for ReportLab"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    def title_to_filename(self, title: str) -> str:
        """Convert title to a safe filename"""
        # Remove special characters and replace spaces with underscores
        filename = re.sub(r'[^\w\s-]', '', title)
        filename = re.sub(r'[-\s]+', '_', filename)
        return filename.lower() + '.pdf'
    
    def create_pdf_diff(self, file1_path: str, file2_path: str, output_path: Optional[str] = None, title: str = "Beautiful Python Diff") -> str:
        """Create a beautiful PDF diff between two Python files"""
        
        # Read files
        try:
            with open(file1_path, 'r', encoding='utf-8') as f:
                file1_lines = f.readlines()
            with open(file2_path, 'r', encoding='utf-8') as f:
                file2_lines = f.readlines()
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
        
        # Create diff
        differ = difflib.unified_diff(
            file1_lines, file2_lines,
            fromfile=file1_path, tofile=file2_path,
            lineterm='', n=3
        )
        
        diff_lines = list(differ)
        
        # Count changes
        added_lines = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        removed_lines = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        
        # Set output path - use title-based filename if no output specified
        if not output_path:
            output_path = self.title_to_filename(title)
        
        # Generate PDF
        self._generate_pdf(
            file1_path, file2_path, file1_lines, file2_lines,
            added_lines, removed_lines, output_path, title
        )
        
        return output_path
    
    def _generate_pdf(self, file1_path: str, file2_path: str,
                     file1_lines: List[str], file2_lines: List[str],
                     added_lines: int, removed_lines: int, output_path: str, title: str):
        """Generate the PDF document"""
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        # Build content
        story = []
        
        # Header section with colored background
        file1_name = Path(file1_path).name
        file2_name = Path(file2_path).name
        
        # Create header table with background color
        header_data = [
            [Paragraph(f"📊 {title}", self.styles['CustomTitle'])],
            [Paragraph(f"<b>Baseline:</b> {self.escape_text(file1_path)}", self.styles['FileInfo'])],
            [Paragraph(f"<b>Modified:</b> {self.escape_text(file2_path)}", self.styles['FileInfo'])],
            [Paragraph(f"<font color='#28a745'>+{added_lines}</font> | <font color='#dc3545'>-{removed_lines}</font> | Total lines: {max(len(file1_lines), len(file2_lines))}", self.styles['Stats'])]
        ]
        
        header_table = Table(header_data, colWidths=[doc.width])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['header_bg']),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 12))
        
        # Legend
        legend_data = [
            [
                Paragraph("<font color='#28a745'>■</font> Added lines", self.styles['Normal']),
                Paragraph("<font color='#dc3545'>■</font> Removed lines", self.styles['Normal']),
                Paragraph("□ Unchanged lines", self.styles['Normal'])
            ]
        ]
        
        legend_table = Table(legend_data, colWidths=[doc.width/3, doc.width/3, doc.width/3])
        legend_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 1, HexColor('#e9ecef')),
        ]))
        
        story.append(legend_table)
        story.append(Spacer(1, 12))
        
        # Generate diff content
        diff_table_data, row_types = self._create_diff_table_data(file1_lines, file2_lines)
        
        # Create table
        if diff_table_data:
            table = Table(diff_table_data, colWidths=[25*mm, doc.width-25*mm])
            table.setStyle(self._get_table_style(row_types))
            story.append(table)
        
        # Footer
        story.append(Spacer(1, 12))
        footer_text = "Generated by Beautiful Python Diff Viewer • Made with ❤️ for clean code comparison"
        story.append(Paragraph(footer_text, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        print(f"✨ Beautiful PDF diff saved to: {output_path}")
    
    def _create_diff_table_data(self, file1_lines: List[str], file2_lines: List[str]) -> tuple:
        """Create table data for the diff and return both data and row types"""
        
        matcher = difflib.SequenceMatcher(None, file1_lines, file2_lines)
        table_data = []
        row_types = []
        line_num = 1
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Unchanged lines
                for i in range(i1, i2):
                    line_content = self.escape_text(file1_lines[i].rstrip('\n'))
                    # Wrap long lines
                    if len(line_content) > 90:
                        wrapped_lines = textwrap.wrap(line_content, width=90)
                        for j, wrapped_line in enumerate(wrapped_lines):
                            line_num_display = str(line_num) if j == 0 else ""
                            table_data.append([
                                Paragraph(line_num_display, self.styles['LineNumber']),
                                Paragraph(wrapped_line, self.styles['CodeUnchanged'])
                            ])
                            row_types.append('unchanged')
                    else:
                        table_data.append([
                            Paragraph(str(line_num), self.styles['LineNumber']),
                            Paragraph(line_content, self.styles['CodeUnchanged'])
                        ])
                        row_types.append('unchanged')
                    line_num += 1
            
            elif tag == 'delete':
                # Removed lines
                for i in range(i1, i2):
                    line_content = self.escape_text(file1_lines[i].rstrip('\n'))
                    if len(line_content) > 88:  # Account for "- " prefix
                        wrapped_lines = textwrap.wrap(line_content, width=88)
                        for j, wrapped_line in enumerate(wrapped_lines):
                            line_num_display = str(line_num) if j == 0 else ""
                            prefix = "- " if j == 0 else "  "
                            table_data.append([
                                Paragraph(line_num_display, self.styles['LineNumber']),
                                Paragraph(prefix + wrapped_line, self.styles['CodeRemoved'])
                            ])
                            row_types.append('removed')
                    else:
                        table_data.append([
                            Paragraph(str(line_num), self.styles['LineNumber']),
                            Paragraph("- " + line_content, self.styles['CodeRemoved'])
                        ])
                        row_types.append('removed')
                    line_num += 1
            
            elif tag == 'insert':
                # Added lines
                for j in range(j1, j2):
                    line_content = self.escape_text(file2_lines[j].rstrip('\n'))
                    if len(line_content) > 88:  # Account for "+ " prefix
                        wrapped_lines = textwrap.wrap(line_content, width=88)
                        for k, wrapped_line in enumerate(wrapped_lines):
                            line_num_display = str(line_num) if k == 0 else ""
                            prefix = "+ " if k == 0 else "  "
                            table_data.append([
                                Paragraph(line_num_display, self.styles['LineNumber']),
                                Paragraph(prefix + wrapped_line, self.styles['CodeAdded'])
                            ])
                            row_types.append('added')
                    else:
                        table_data.append([
                            Paragraph(str(line_num), self.styles['LineNumber']),
                            Paragraph("+ " + line_content, self.styles['CodeAdded'])
                        ])
                        row_types.append('added')
                    line_num += 1
            
            elif tag == 'replace':
                # Changed lines - show removed first, then added
                for i in range(i1, i2):
                    line_content = self.escape_text(file1_lines[i].rstrip('\n'))
                    if len(line_content) > 88:
                        wrapped_lines = textwrap.wrap(line_content, width=88)
                        for j, wrapped_line in enumerate(wrapped_lines):
                            line_num_display = str(line_num) if j == 0 else ""
                            prefix = "- " if j == 0 else "  "
                            table_data.append([
                                Paragraph(line_num_display, self.styles['LineNumber']),
                                Paragraph(prefix + wrapped_line, self.styles['CodeRemoved'])
                            ])
                            row_types.append('removed')
                    else:
                        table_data.append([
                            Paragraph(str(line_num), self.styles['LineNumber']),
                            Paragraph("- " + line_content, self.styles['CodeRemoved'])
                        ])
                        row_types.append('removed')
                    line_num += 1
                
                for j in range(j1, j2):
                    line_content = self.escape_text(file2_lines[j].rstrip('\n'))
                    if len(line_content) > 88:
                        wrapped_lines = textwrap.wrap(line_content, width=88)
                        for k, wrapped_line in enumerate(wrapped_lines):
                            line_num_display = str(line_num) if k == 0 else ""
                            prefix = "+ " if k == 0 else "  "
                            table_data.append([
                                Paragraph(line_num_display, self.styles['LineNumber']),
                                Paragraph(prefix + wrapped_line, self.styles['CodeAdded'])
                            ])
                            row_types.append('added')
                    else:
                        table_data.append([
                            Paragraph(str(line_num), self.styles['LineNumber']),
                            Paragraph("+ " + line_content, self.styles['CodeAdded'])
                        ])
                        row_types.append('added')
                    line_num += 1
        
        return table_data, row_types
    
    def _get_table_style(self, row_types: List[str]) -> TableStyle:
        """Get table style with diff highlighting"""
        
        style_commands = [
            ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e9ecef')),
        ]
        
        # Add background colors based on line type
        for i, line_type in enumerate(row_types):
            if line_type == 'added':
                style_commands.append(('BACKGROUND', (1, i), (1, i), self.colors['added_bg']))
            elif line_type == 'removed':
                style_commands.append(('BACKGROUND', (1, i), (1, i), self.colors['removed_bg']))
            
            # Always color line number column
            style_commands.append(('BACKGROUND', (0, i), (0, i), self.colors['line_number_bg']))
        
        return TableStyle(style_commands)


def main():
    parser = argparse.ArgumentParser(
        description="🎨 Create beautiful PDF diffs for Python files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python_diff_pdf_simple.py file1.py file2.py
  python_diff_pdf_simple.py file1.py file2.py -o output.pdf
  python_diff_pdf_simple.py file1.py file2.py -t "My Analysis"
  python_diff_pdf_simple.py /path/to/baseline.py /path/to/modified.py -t "Code Review"
        """
    )
    
    parser.add_argument('file1', help='Path to the baseline/original file')
    parser.add_argument('file2', help='Path to the modified/new file')
    parser.add_argument('-o', '--output', 
                       help='Output PDF file path (default: auto-generated from title)',
                       default=None)
    parser.add_argument('-t', '--title',
                       help='Custom title for the diff report (default: Beautiful Python Diff)',
                       default='Beautiful Python Diff')
    
    args = parser.parse_args()
    
    # Validate files exist
    if not Path(args.file1).exists():
        print(f"❌ Error: File '{args.file1}' not found")
        sys.exit(1)
    
    if not Path(args.file2).exists():
        print(f"❌ Error: File '{args.file2}' not found")
        sys.exit(1)
    
    print(f"🔍 Comparing files:")
    print(f"   Baseline: {args.file1}")
    print(f"   Modified: {args.file2}")
    print(f"📝 Generating beautiful PDF diff...")
    
    # Create diff
    generator = SimpleDiffPDFGenerator()
    output_path = generator.create_pdf_diff(args.file1, args.file2, args.output, args.title)
    
    print(f"🎉 Done! PDF saved as '{output_path}'")


if __name__ == '__main__':
    main()
