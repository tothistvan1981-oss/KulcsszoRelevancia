import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from timodule import *



def TI_letolt_oldal(url):
    try:
        start = time.time()
        r = requests.get(url, timeout=7, headers={'User-Agent': 'Mozilla/5.0'})
        elapsed = time.time() - start
        if r.status_code == 200:
            return r.text, elapsed
        return "", elapsed
    except:
        return "", 0


def TI_osszes_elemzes(base_url, maxoldal=5):
    html, load_time = TI_letolt_oldal(base_url)
    if not html:
        return []
    belsok = TI_belso_linkek(base_url, html)
    urls = [base_url]
    eredmenyek = []
    for u in belsok:
        if u not in urls and len(urls) < maxoldal:
            urls.append(u)
    for url in urls:
        html, load_time = TI_letolt_oldal(url)
        if not html:
            continue
        desc, keys, szoveg, title = TI_kigyujt_meta_es_szoveg(html)
        kulcs = TI_szovegbol_kulcsszavak(szoveg)
        eredmenyek.append(TIEredmeny(url, desc, keys, kulcs, title, load_time))
    return eredmenyek

def TI_gui_megjelenit(eredmenyek):
    for widget in result_frame.winfo_children():
        widget.destroy()
    if not eredmenyek:
        ttk.Label(result_frame, text="Nincs elemzés.").pack()
        return
    for e in eredmenyek:
        ttk.Label(result_frame, text=f"\nURL: {e.url}", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(result_frame, text="Meta leírás: " + e.description).pack(anchor="w")
        ttk.Label(result_frame, text="Meta kulcsszavak: " + (", ".join(e.key_szavak) if e.key_szavak else "(nincs)")).pack(anchor="w")
        ttk.Label(result_frame, text=f"Meta leírás relevancia: {e.relev_desc}%, kulcsszó relevancia: {e.relev_keys}%").pack(anchor="w")
        ttk.Label(result_frame, text="Top tartalom kulcsszavak: " + ", ".join([k for k, _ in e.szoveg_kulcs.most_common(5)])).pack(anchor="w")
        text = f"Oldal betöltési ideje: {e.load_time:.2f} másodperc."
        if e.load_time > 2:
            text += " Figyelem: Lassú oldalbetöltés! (SEO szempontból optimalizálandó)"
        ttk.Label(result_frame, text=text).pack(anchor="w")
        tippek = TI_seo_tippek(e.title, e.description)
        for tipp in tippek:
            ttk.Label(result_frame, text="SEO tipp: " + tipp, foreground="orange").pack(anchor="w")

    top_kulcs, meta_relev = TI_osszesitett_stat(eredmenyek)
    ttk.Label(result_frame, text="\nÖsszesített TOP kulcsszavak: " + ", ".join([k for k, _ in top_kulcs[:10]]), font=("Arial", 10)).pack(anchor="w")


def TI_elemzes_gomb():
    url = url_entry.get().strip()
    if not url.startswith("https"):
        url = "https://" + url
    btn.config(state="disabled")
    eredmenyek = TI_osszes_elemzes(url, maxoldal=5)
    if not eredmenyek:
        messagebox.showerror("Hiba", "Nem sikerült letölteni a weboldalt vagy nincs adat!")
    else:
        TI_gui_megjelenit(eredmenyek)
        root.ti_eredmenyek = eredmenyek
    btn.config(state="normal")

root = tk.Tk()
root.title("TI Kulcsszó relevancia")
root.geometry("800x800")

mainframe = ttk.Frame(root, padding=10)
mainframe.pack(fill="both", expand=True)

ttk.Label(mainframe, text="Adj meg egy domaint (pl. alkossegyedit.hu vagy https://alkossegyedit.hu):", font=("Arial", 12)).pack(anchor="w")
url_entry = ttk.Entry(mainframe, width=50)
url_entry.pack(anchor="w")
btn = ttk.Button(mainframe, text="Elemzés indítása", command=TI_elemzes_gomb)
btn.pack(anchor="w", pady=8)

canvas = tk.Canvas(mainframe)
scroll_y = tk.Scrollbar(mainframe, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scroll_y.set)
scroll_y.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
result_frame = ttk.Frame(canvas)
result_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=result_frame, anchor="nw")
canvas.configure(yscrollcommand=scroll_y.set)

root.mainloop()
