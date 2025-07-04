import duckdb
from shiny import module, reactive, render, ui

default_query = "SELECT region,class,medication,min_dose,max_dose,min_freq,max_freq from meds ORDER By class, medication LIMIT 10"



@module.ui
def query_output_ui(remove_id, qry=default_query):
    return (
        ui.card(
            {"id": remove_id},
            ui.card_header(f"{remove_id}"),
            ui.layout_columns(
                [
                    ui.input_text_area(
                        "sql_query",
                        "",
                        value=qry,
                        width="100%",
                        height="200px",
                    ),
                    ui.layout_columns(
                        ui.input_action_button("run", "Run", class_="btn btn-primary"),
                        ui.input_action_button("export", "Export", class_="btn"),
                        ui.input_action_button(
                            "rmv", "Remove", class_="btn btn-warning"
                        )
                    ),
                ]
            ),
                ui.output_data_frame("results"),
        )
    )


@module.server
def query_output_server(
    input, output, session, con: duckdb.DuckDBPyConnection, remove_id
):
    @render.data_frame
    @reactive.event(input.run)
    def results():
        qry = input.sql_query().replace("\n", " ")
        return con.query(qry).to_df()
    
    @reactive.effect
    @reactive.event(input.export)
    def export_query():
        existing_query = input.sql_query()
        csv_output_query = "COPY ("+f"{existing_query}"+") TO 'output.csv' (HEADER, DELIMITER ',')"
        con.sql(csv_output_query)
        excel_output_query = "COPY ("+f"{existing_query}"+") TO 'output.xlsx' with (FORMAT XSLS)"
        con.sql(excel_output_query)
  
    @reactive.effect
    @reactive.event(input.rmv)
    def _():
        ui.remove_ui(selector=f"div#{remove_id}")

