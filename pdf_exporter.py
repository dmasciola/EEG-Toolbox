import io
from fpdf import FPDF


class PDFReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, 'EEG Toolbox - Signal Processing Report', border=False, ln=1, align='C')
        
        self.set_font('helvetica', 'I', 11)
        self.cell(0, 8, 'Version 2.0 | developed by Davide Masciola', border=False, ln=1, align='C')
        
        #self.set_line_width(0.5)
        #self.line(10, 30, 200, 30)
        self.ln(5)



def generate_pdf(report_log: dict, figures: dict) -> bytes:
    pdf = PDFReport()
    pdf.alias_nb_pages() 
    pdf.add_page()
    
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "1. Pipeline Log", ln=1)
    
    pdf.set_font("helvetica", "", 11)
    for step, description in report_log.items():
        pdf.set_font("helvetica", "B", 11)
        pdf.write(8, f"{step}: ")
        
        pdf.set_font("helvetica", "", 11)
        pdf.write(8, f"{description}\n\n")
    
    pdf.ln(5)

    # --- GRAPHS ---
   
    pdf.add_page()
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "2. Visualizations", ln=1)
    
    is_first_figure = True

    for title, fig in figures.items():
            
        if not is_first_figure:
            pdf.add_page()  

        is_first_figure = False     
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 5, title, ln=1)
        
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
        img_buffer.seek(0)
        
        pdf.image(img_buffer, w=190)



        
    # Return raw PDF bytes
    return bytes(pdf.output())