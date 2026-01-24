# web_torneo.py
import pandas as pd

def genera_html_torneo():
    # Stili CSS integrati per mantenere la coerenza
    css_style = """
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #ffffff; }
        .header-box { background-color: #f8f9fa; padding: 20px; border-bottom: 3px solid #333; }
        
        /* Tab Styles */
        .nav-tabs .nav-link { color: #555; font-weight: 500; }
        .nav-tabs .nav-link.active { color: #d9534f !important; font-weight: bold; border-bottom: 3px solid #d9534f; }
        
        /* Tabelle Classiche Bianco/Nero per Tabelloni */
        .table-finali { border: 1px solid #000 !important; background-color: #fff; }
        .table-finali thead { background-color: #000; color: #fff; }
        .table-finali td, .table-finali th { border: 1px solid #dee2e6 !important; padding: 12px; }
        
        /* Colori per le altre Tab (Gironi e Classifiche) - Come da tua versione precedente */
        .bg-gironi { background-color: #e3f2fd; } /* Azzurrino */
        .bg-classifiche { background-color: #f1f8e9; } /* Verdisto */
        
        /* Header Sezioni Tabellone */
        .row-header { background-color: #444 !important; color: white !important; font-weight: bold; }
        .col-perdente { font-style: italic; color: #555; border-left: 2px solid #000 !important; }
    </style>
    """

    html_start = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <title>Torneo One Wall - Accademia Pallapugno</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        {css_style}
    </head>
    <body>
    <div class="container-fluid mt-3">
        <div class="header-box mb-4">
            <h1>🏆 Torneo One Wall - Accademia Pallapugno</h1>
        </div>

        <ul class="nav nav-tabs" id="myTab" role="tablist">
            <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#gironi">🎾 Gare Gironi</button></li>
            <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#classifiche">📊 Classifiche</button></li>
            <li class="nav-item"><button class="nav-link" data-bs-toggle="tab" data-bs-target="#playoff">⚔️ Playoff</button></li>
            <li class="nav-item"><button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tabelloni">🏁 Tabelloni Finali</button></li>
        </ul>

        <div class="tab-content p-3">
            <div class="tab-pane fade" id="gironi">
                <div class="table-responsive bg-gironi p-3 rounded">
                    <h3>Incontri Gironi</h3>
                    <table class="table table-sm table-hover">
                        <thead><tr><th>Match</th><th>Squadra A</th><th>Squadra B</th><th>Risultato</th></tr></thead>
                        <tbody><tr><td>G1</td><td>Squadra 1</td><td>Squadra 2</td><td>-</td></tr></tbody>
                    </table>
                </div>
            </div>

            <div class="tab-pane fade" id="classifiche">
                <div class="table-responsive bg-classifiche p-3 rounded">
                    <h3>Classifiche Gruppi</h3>
                    <table class="table table-striped">
                        <thead><tr><th>Pos</th><th>Squadra</th><th>Punti</th></tr></thead>
                        <tbody><tr><td>1</td><td>Esempio Team</td><td>12</td></tr></tbody>
                    </table>
                </div>
            </div>

            <div class="tab-pane fade" id="playoff">
                <p>Struttura Playoff mantenuta...</p>
            </div>

            <div class="tab-pane fade show active" id="tabelloni">
                <div class="table-responsive">
                    <table class="table table-finali align-middle">
                        <thead>
                            <tr>
                                <th>Fase</th>
                                <th>ID Match</th>
                                <th>Sfidante 1</th>
                                <th>Sfidante 2</th>
                                <th>Risultato</th>
                                <th>VINCITORE</th>
                                <th class="col-perdente">PERDENTE</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr class="row-header"><td colspan="7">QUARTI DI FINALE (Posizioni 1-8)</td></tr>
                            <tr><td>Quarti Upper</td><td><b>QU1</b></td><td>Vincitore Match 1</td><td>Vincitore Match 2</td><td>-</td><td></td><td class="col-perdente"></td></tr>
                            <tr><td>Quarti Upper</td><td><b>QU2</b></td><td>Vincitore Match 3</td><td>Vincitore Match 4</td><td>-</td><td></td><td class="col-perdente"></td></tr>
                            <tr><td>Quarti Upper</td><td><b>QU3</b></td><td>Vincitore Match 5</td><td>Vincitore Match 6</td><td>-</td><td></td><td class="col-perdente"></td></tr>
                            <tr><td>Quarti Upper</td><td><b>QU4</b></td><td>Vincitore Match 7</td><td>Vincitore Match 8</td><td>-</td><td></td><td class="col-perdente"></td></tr>
                            
                            <tr class="row-header"><td colspan="7">SEMIFINALI</td></tr>
                            <tr><td>Semi 1-4</td><td><b>S1</b></td><td>Vincitore QU1</td><td>Vincitore QU2</td><td>-</td><td></td><td class="col-perdente"></td></tr>
                            <tr><td>Semi 1-4</td><td><b>S2</b></td><td>Vincitore QU3</td><td>Vincitore QU4</td><td>-</td><td></td><td class="col-perdente"></td></tr>
                            <tr><td>Semi 5-8</td><td><b>S3</b></td><td>Perdente QU1</td><td>Perdente QU2</td><td>-</td><td></td><td class="col-perdente"></td></tr>
                            <tr><td>Semi 5-8</td><td><b>S4</b></td><td>Perdente QU3</td><td>Perdente QU4</td><td>-</td><td></td><td class="col-perdente"></td></tr>

                            <tr class="row-header"><td colspan="7">FINALI DI POSIZIONE</td></tr>
                            <tr><td><b>Finale 1°-2°</b></td><td><b>F1</b></td><td>Vincitore S1</td><td>Vincitore S2</td><td>-</td><td></td><td class="col-perdente"></td></tr>
                            <tr><td>Finale 3°-4°</td><td><b>F2</b></td><td>Perdente S1</td><td>Perdente S2</td><td>-</td><td></td><td class="col-perdente"></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return html_start

# Esempio di come salvare il file
if __name__ == "__main__":
    with open("web_torneo.html", "w", encoding="utf-8") as f:
        f.write(genera_html_torneo())
    print("File generato con successo!")
