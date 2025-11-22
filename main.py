import tkinter as tk
from tkinter import ttk, messagebox
from timodule import TIAnalyzer
from tidatabase import TI_Adatbazis


analyzer = TIAnalyzer()

def TI_gui_megjelenit(eredmenyek):
    if not eredmenyek:
        ttk.Label(result_frame, text="Nincs elemzés.").grid(column=0, row=0, padx=5, pady=5, sticky="w")
        return
    for widget in result_frame.winfo_children():
        widget.destroy()
    sor = 0
    for e in eredmenyek:
        ttk.Label(result_frame, text=f"URL: {e.url}",
                  font=("Arial", 10, "bold")).grid(column=0, row=sor, padx=5, pady=5, sticky="w")
        sor += 1

        ttk.Label(result_frame, text="Meta leírás: " + e.description)\
            .grid(column=0, row=sor, padx=5, pady=2, sticky="w")
        sor += 1

        ttk.Label(result_frame,
                  text="Meta kulcsszavak: " +
                       (", ".join(e.key_szavak) if e.key_szavak else "(nincs)"))\
            .grid(column=0, row=sor, padx=5, pady=2, sticky="w")
        sor += 1

        ttk.Label(result_frame,
                  text=f"Relevancia: DESC: {e.relev_desc}%, KEY: {e.relev_keys}%")\
            .grid(column=0, row=sor, padx=5, pady=2, sticky="w")
        sor += 1

        ttk.Label(result_frame,
                  text="Top kulcsszavak: " +
                       ", ".join([k for k, _ in e.szoveg_kulcs.most_common(5)]))\
            .grid(column=0, row=sor, padx=5, pady=2, sticky="w")
        sor += 1

        text = f"Betöltési idő: {e.load_time:.2f} mp"
        if e.load_time > 2:
            text += " (Lassú betöltés!)"

        ttk.Label(result_frame, text=text)\
            .grid(column=0, row=sor, padx=5, pady=2, sticky="w")
        sor += 1


        for tipp in analyzer.TI_seo_tippek(e.title, e.description):
            ttk.Label(result_frame, text="SEO tipp: " + tipp, foreground="orange")\
                .grid(column=0, row=sor, padx=5, pady=2, sticky="w")
            sor += 1

        ttk.Label(result_frame, text="-" * 80).grid(column=0, row=sor, padx=5, pady=10, sticky="w")
        sor += 1

    top_kulcs, _ = analyzer.TI_osszesitett_stat(eredmenyek)
    ttk.Label(result_frame,
              text="Összesített TOP kulcsszavak: " +
                   ", ".join([k for k, _ in top_kulcs[:10]]),
              font=("Arial", 10, "bold"))\
        .grid(column=0, row=sor, padx=5, pady=10, sticky="w")


def TI_betolt_mentett():
    eredmenyek = []
    mentettek = db.TI_leker_utolso(limit=10)
    if not mentettek:
        messagebox.showinfo("Nincs adat", "Az adatbázis üres.")
        return
    uzenet = "Legutóbbi mentett adatok \n"
    for sor in mentettek:
        elemzes_id, url, title, desc, relev_desc, relev_keys, load_time, datum = sor

        uzenet += f"ID: {elemzes_id}\n"
        uzenet += f"URL: {url}\n"
        uzenet += f"Title: {title}\n"
        uzenet += f"Meta-leírás: {desc}\n"

        kulcsszavak = db.TI_leker_kulcsszavak(elemzes_id)
        if kulcsszavak:
            kw_str = ", ".join([f"{szo}({db})" for szo, db in kulcsszavak])
            uzenet += f"Kulcsszavak: {kw_str}\n"

        uzenet += f"Relevancia: DESC {relev_desc}%, KEY {relev_keys}%\n"
        uzenet += f"Betöltési idő: {load_time:.2f} mp\n"
        uzenet += f"Dátum: {datum}\n"
        uzenet += "-" * 60 + "\n"

    for widget in result_frame.winfo_children():
        widget.destroy()
    ttk.Label(result_frame,
              text=uzenet).grid(column=0, row=1, padx=5, pady=10, sticky="w")


def TI_elemzes_gomb():
    url = url_entry.get().strip()
    if not url.startswith("https"):
        url = "https://" + url

    btn.config(state="disabled")
    try:
        max_page = int(max_page_bemenet.get())
    except:
        max_page = 5
        max_page_bemenet.set("5")

    eredmenyek = analyzer.TI_osszes_elemzes(url, max_page)

    if not eredmenyek:
        messagebox.showerror("Hiba", "Nem sikerült letölteni az oldalt!")
    else:
        TI_gui_megjelenit(eredmenyek)
        for e in eredmenyek:
            db.TI_mentes_eredmeny(e)
    btn.config(state="normal")

db = TI_Adatbazis()
root = tk.Tk()
root.title("TI Kulcsszó relevancia")
root.geometry("900x800")

mainframe = ttk.Frame(root, padding=10)
mainframe.grid(column=0, row=0, sticky="nsew")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

ttk.Label(
    mainframe,
    text="Adj meg egy domaint (pl: hvg.hu):",
    font=("Arial", 12)
).grid(column=0, row=0, padx=10, pady=10, sticky="w")

url_entry = ttk.Entry(mainframe, width=50)
url_entry.grid(column=0, row=1, padx=10, pady=5, sticky="w")

ttk.Label(
    mainframe,
    text="Maximum szint:",
    font=("Arial", 12)
).grid(column=1, row=0, padx=10, pady=10, sticky="w")

max_page_bemenet = tk.StringVar(value="5")
max_page = ttk.Entry(mainframe, width=5, textvariable=max_page_bemenet)
max_page.grid(column=1, row=1, padx=10, pady=5, sticky="w")

btn = ttk.Button(mainframe, text="Élő elemzés indítása", command=TI_elemzes_gomb)
btn.grid(column=2, row=1, padx=10, pady=5, sticky="w")

btn_load = ttk.Button(mainframe, text="Mentett elemzés betöltése", command=TI_betolt_mentett)
btn_load.grid(column=3, row=1, padx=10, pady=5, sticky="w")

canvas = tk.Canvas(mainframe)
scroll_y = tk.Scrollbar(mainframe, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scroll_y.set)

canvas.grid(column=0, row=2, columnspan=2, sticky="nsew")
scroll_y.grid(column=2, row=2, sticky="ns")

mainframe.rowconfigure(2, weight=1)
mainframe.columnconfigure(0, weight=1)

result_frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=result_frame, anchor="nw")

result_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

root.mainloop()
