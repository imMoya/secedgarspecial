from secedgarspecial import SECDataProcessor

if __name__ == "__main__":
    # Odd Lots processing
    odd_lots_processor = SECDataProcessor(
        folder="db_oddlots", 
        html_folder="html", 
        search_term="odd lots", 
        filters="Tender offer statement", 
        filter_field="form_name"
    )
    odd_lots_processor.run()

    # Spin-Offs processing
    spin_offs_processor = SECDataProcessor(
        folder="db_spinoffs", 
        html_folder="html", 
        search_term="the", 
        filters="991", 
        filter_field="filing_document_url", 
        forms="['10-12B']"
    )
    spin_offs_processor.run()