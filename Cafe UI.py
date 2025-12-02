# FULL UPDATED VERSION USING transaksi.csv & detail_transaksi.csv
# (Complete from start to finish — no truncation)

from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import csv
import datetime
from functools import partial
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


login_window = Tk()
login_window.title("Python Cafe - Login")
login_window.geometry("800x600")
login_window.configure(bg="#F2DFD7")

# ======================================================
# LOGIN
# ======================================================

def login(username_input, password_input):
    with open("users.csv", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username_input and row["password"] == password_input:
                return row
    return None

# ======================================================
# MENU DATA
# ======================================================

def load_menu_data():
    data = []
    with open("menu.csv", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for r in reader:
            r['id'] = int(r['id'])
            r['stok'] = int(r['stok'])
            r['harga'] = int(r['harga'])
            data.append(r)
    return data

def update_menu(menu_items):
    # gunakan header yang konsisten agar CSV selalu sama formatnya
    fieldnames = ["id", "nama", "harga", "stok", "foto"]
    # pastikan kita menulis field sesuai urutan fieldnames
    with open("menu.csv", "w", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        rows = []
        for m in menu_items:
            row = {
                "id": int(m.get("id", 0)),
                "nama": m.get("nama", ""),
                "harga": int(m.get("harga", 0)),
                "stok": int(m.get("stok", 0)),
                "foto": m.get("foto", "")
            }
            rows.append(row)
        writer.writerows(rows)


# ======================================================
# TRANSAKSI SYSTEM
# ======================================================

# -----------------------------
# REPLACE save_transaksi WITH THIS
# -----------------------------
def save_transaksi(order_id, total_harga, meja, metode="Cash"):
    fieldnames = ["id", "tanggal", "total", "metode_pembayaran", "meja_id", "status"]

    try:
        with open("transaksi.csv", 'x', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
    except FileExistsError:
        pass

    with open("transaksi.csv", 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow({
            "id": order_id,
            "tanggal": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": total_harga,
            "metode_pembayaran": metode,
            "meja_id": meja,
            "status": "Menunggu Konfirmasi"
        })

def save_detail_transaksi(order_id, cart, diskon_persen):
    fieldnames = ["id_transaksi", "id_menu", "nama", "jumlah", "harga", "diskon"]

    try:
        with open("detail_transaksi.csv", 'x', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
    except FileExistsError:
        pass

    with open("detail_transaksi.csv", 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for c in cart:
            writer.writerow({
                "id_transaksi": order_id,
                "id_menu": c['item_id'],
                "nama": c['nama'],
                "jumlah": c['jumlah'],
                "harga": c['harga'],
                "diskon": diskon_persen
            })

# -----------------------------
# REPLACE save_detail_transaksi IF YOU WANT (optional - current is OK)
# (kept as-is, but ensure fieldnames match what you expect)
# -----------------------------


# -----------------------------
# REPLACE load_transaksi_by_status WITH THIS
# -----------------------------
def load_transaksi_by_status(status):
    hasil = {}
    try:
        with open("transaksi.csv", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # gunakan kolom 'status' dan 'id' sesuai header baru
                if row.get('status') == status:
                    hasil[row.get('id')] = row
    except FileNotFoundError:
        return {}
    except Exception:
        return {}
    return hasil


# -----------------------------
# REPLACE update_transaksi_status WITH THIS
# -----------------------------
def update_transaksi_status(order_id, new_status):
    rows = []
    fieldnames = ["id", "tanggal", "total", "metode_pembayaran", "meja_id", "status"]
    try:
        with open("transaksi.csv", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('id') == order_id:
                    row['status'] = new_status
                rows.append(row)
    except FileNotFoundError:
        return

    # tulis ulang file
    with open("transaksi.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def set_transaksi_lunas(order_id, metode_pembayaran="Cash"):
    """Set transaksi jadi Lunas dan update metode pembayaran jika diberikan."""
    rows = []
    fieldnames = ["id", "tanggal", "total", "metode_pembayaran", "meja_id", "status"]
    try:
        with open("transaksi.csv", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("id") == order_id:
                    row["status"] = "Lunas"
                    row["metode_pembayaran"] = metode_pembayaran
                rows.append(row)
    except FileNotFoundError:
        return False

    with open("transaksi.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return True



# -----------------------------
# REPLACE get_meja_dipakai WITH THIS
# -----------------------------
def get_meja_dipakai():
    meja_terpakai = set()
    try:
        with open("transaksi.csv", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # cek status yang masih aktif, lalu ambil meja_id (bukan 'meja')
                if row.get("status") in ["Menunggu Konfirmasi", "Disiapkan"]:
                    m = row.get("meja_id")
                    if m:
                        meja_terpakai.add(m)
    except FileNotFoundError:
        pass
    except Exception:
        pass
    return meja_terpakai

def load_transaksi_harian():
    hasil = []
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    try:
        with open("transaksi.csv", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("tanggal", "").startswith(today):
                    hasil.append(row)
    except FileNotFoundError:
        return []
    
    return hasil

def total_pendapatan_hari_ini():
    data = []
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        with open("transaksi.csv", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("tanggal", "").startswith(today) and row.get("status") == "Lunas":
                    data.append(row)
    except FileNotFoundError:
        return 0

    total = 0
    for row in data:
        try:
            total += int(row.get("total", 0))
        except:
            pass
    return total


# ======================================================
# ORDER PAGE
# ======================================================

# ======================================================
# ORDER PAGE (UPDATED: remove item, qty adjust, discount display)
# ======================================================
# ======================================================
# ORDER PAGE (FINAL FIXED VERSION)
# ======================================================
def order():
    win = Toplevel(login_window)
    win.title("Menu Pesanan")
    win.geometry("900x600")
    win.configure(bg="#F2DFD7")

    cart = []

    # LEFT = menu, RIGHT = cart
    menu_frame = Frame(win, bg="#F2DFD7")
    menu_frame.pack(side="left", fill="both", expand=True)

    cart_frame = Frame(win, bg="white", width=300)
    cart_frame.pack(side="right", fill="y")
    cart_frame.pack_propagate(False)

    Label(cart_frame, text="Keranjang", font=("Arial", 16), bg="white").pack(pady=10)

    # DISKON
    Label(cart_frame, text="Kode Diskon:", bg="white").pack()
    diskon_entry = Entry(cart_frame, font=("Arial", 12), width=18)
    diskon_entry.pack(pady=(0, 10))

    # PILIH MEJA
    Label(cart_frame, text="Pilih Meja:", bg="white").pack()

    meja_var = StringVar()
    meja_semua = ["Meja 1", "Meja 2", "Meja 3", "Meja 4", "Meja 5"]

    def refresh_meja_options():
        meja_terpakai = get_meja_dipakai()
        return [m for m in meja_semua if m not in meja_terpakai]

    meja_list = refresh_meja_options()
    meja_box = ttk.Combobox(cart_frame, textvariable=meja_var, values=meja_list, state="readonly", width=15)
    meja_box.pack(pady=(0, 10))

    if meja_list:
        meja_box.current(0)
    else:
        meja_box.set("Tidak Ada Meja")
        meja_box.config(state="disabled")

    # CART BOX
    cart_box = Frame(cart_frame, bg="white")
    cart_box.pack(fill="both", expand=True, padx=8)

    total_label = Label(cart_frame, text="Total: Rp 0", bg="white", font=("Arial", 12))
    total_label.pack(pady=8)

    diskon_info_label = Label(cart_frame, text="", bg="white", font=("Arial", 10))
    diskon_info_label.pack()

    KODE_DISKON = {"CAFE10%": 10, "PROMO50": 50, "VIP30": 30}

    # =====================================================================
    # REFRESH CART
    # =====================================================================
    def refresh_cart():
        for w in cart_box.winfo_children():
            w.destroy()

        total = 0

        if not cart:
            Label(cart_box, text="Keranjang Kosong", bg="white").pack()
        else:
            for i, c in enumerate(cart):
                row = Frame(cart_box, bg="white")
                row.pack(fill="x", pady=4)

                Label(row, text=c["nama"], bg="white").pack(side="left", padx=6)
                Label(row, text=f"Rp {c['harga']}", bg="white").pack(side="left", padx=6)
                Label(row, text=f"x{c['jumlah']}", bg="white").pack(side="left", padx=6)

                ctrl = Frame(row, bg="white")
                ctrl.pack(side="right")

                # + Button
                def plus(idx=i):
                    menus = load_menu_data()
                    for m in menus:
                        if m["id"] == cart[idx]["item_id"]:
                            if m["stok"] <= 0:
                                return
                            m["stok"] -= 1
                            cart[idx]["jumlah"] += 1
                            update_menu(menus)
                            build_menu()
                            refresh_cart()
                            return

                # - Button
                def minus(idx=i):
                    menus = load_menu_data()
                    for m in menus:
                        if m["id"] == cart[idx]["item_id"]:
                            m["stok"] += 1
                            cart[idx]["jumlah"] -= 1
                            if cart[idx]["jumlah"] <= 0:
                                cart.pop(idx)
                            update_menu(menus)
                            build_menu()
                            refresh_cart()
                            return

                # REMOVE Button
                def remove(idx=i):
                    qty = cart[idx]["jumlah"]
                    menus = load_menu_data()
                    for m in menus:
                        if m["id"] == cart[idx]["item_id"]:
                            m["stok"] += qty
                    update_menu(menus)
                    cart.pop(idx)
                    build_menu()
                    refresh_cart()

                Button(ctrl, text="+", width=3, command=plus).pack(side="left", padx=2)
                Button(ctrl, text="-", width=3, command=minus).pack(side="left", padx=2)
                Button(ctrl, text="Hapus", command=remove).pack(side="left", padx=4)

                total += c['harga'] * c['jumlah']

        kode = diskon_entry.get().upper().strip()
        persen = KODE_DISKON.get(kode, 0)
        potongan = int(total * persen / 100)
        total_akhir = total - potongan

        if persen > 0:
            diskon_info_label.config(text=f"Diskon {persen}% (-Rp {potongan})")
        else:
            diskon_info_label.config(text="")

        total_label.config(text=f"Total: Rp {total_akhir}")
        return total_akhir

    # =====================================================================
    # BUILD MENU
    # =====================================================================
    def build_menu():
        for w in menu_frame.winfo_children():
            w.destroy()

        Button(menu_frame, text="Refresh Menu", command=build_menu).pack(pady=6)

        items = load_menu_data()
        for item in items:
            frame = Frame(menu_frame, bg="#F2DFD7")
            frame.pack(fill="x", pady=6)

            # image
            try:
                img = Image.open(item['foto']).resize((140, 110))
                img = ImageTk.PhotoImage(img)
                lbl = Label(frame, image=img, bg="#F2DFD7")
                lbl.image = img
                lbl.pack(side="left", padx=6)
            except:
                Label(frame, text="(No Image)", width=15, height=6, bg="#DDD").pack(side="left", padx=6)

            info = Frame(frame, bg="#F2DFD7")
            info.pack(side="left", padx=10)

            Label(info, text=item["nama"], font=("Arial", 14), bg="#F2DFD7").pack(anchor="w")
            Label(info, text=f"Rp {item['harga']}", bg="#F2DFD7").pack(anchor="w")
            stock_label = Label(info, text=f"Stok: {item['stok']}", bg="#F2DFD7")
            stock_label.pack(anchor="w")

            def add_item(it=item, stok_lbl=stock_label, btn=None):
                menus = load_menu_data()
                for m in menus:
                    if m["id"] == it["id"]:
                        if m["stok"] <= 0:
                            return
                        m["stok"] -= 1
                        it["stok"] = m["stok"]
                        break

                update_menu(menus)

                found = next((x for x in cart if x["item_id"] == it["id"]), None)
                if found:
                    found["jumlah"] += 1
                else:
                    cart.append({
                        "item_id": it["id"],
                        "nama": it["nama"],
                        "harga": it["harga"],
                        "jumlah": 1
                    })

                stok_lbl.config(text=f"Stok: {it['stok']}")
                refresh_cart()

                if it["stok"] <= 0:
                    btn.config(text="Habis", state="disabled")

            btn = Button(frame, text="Tambah")
            btn.config(command=lambda it=item, lbl=stock_label, b=btn: add_item(it, lbl, b))
            if item["stok"] == 0:
                btn.config(text="Habis", state="disabled")
            btn.pack(side="right", padx=10)

    build_menu()
    refresh_cart()

    # =====================================================================
    # CHECKOUT
    # =====================================================================
    def checkout():
        if not cart:
            messagebox.showinfo("Info", "Keranjang kosong!")
            return

        meja_now = meja_var.get()
        if meja_now in get_meja_dipakai():
            messagebox.showwarning("Error", "Meja baru dipakai! Pilih meja lain.")
            return

        total_final = refresh_cart()
        kode = diskon_entry.get().upper().strip()
        persen = KODE_DISKON.get(kode, 0)

        order_id = "TRX-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        save_transaksi(order_id, total_final, meja_now, metode="Belum Dipilih")
        save_detail_transaksi(order_id, cart, persen)

        cart.clear()
        refresh_cart()
        build_menu()

        messagebox.showinfo("Sukses", "Pesanan Berhasil Dibuat!")

    Button(cart_frame, text="Buat Pesanan", font=("Arial", 12, "bold"), command=checkout)\
        .pack(pady=18)





# ======================================================
# KASIR PAGE
# ======================================================

def kasir():
    win = Toplevel(login_window)
    win.title("Halaman Kasir")
    win.geometry("900x600")
    win.configure(bg="#F2DFD7")

    # Laporan ringkas
    laporan_frame = Frame(win, bg="#F2DFD7")
    laporan_frame.pack(fill="x", pady=8)
    Label(laporan_frame, text="Laporan Kasir Hari Ini", font=("Arial", 16, "bold"), bg="#F2DFD7").pack()
    total_label = Label(laporan_frame, text=f"Total Penjualan Hari Ini (Lunas): Rp {total_pendapatan_hari_ini()}", font=("Arial", 12), bg="#F2DFD7")
    total_label.pack(pady=4)
    Button(laporan_frame, text="Refresh Laporan", command=lambda: total_label.config(text=f"Total Penjualan Hari Ini (Lunas): Rp {total_pendapatan_hari_ini()}")).pack()

    Label(win, text="Pesanan Masuk", font=("Arial", 16), bg="#F2DFD7").pack(pady=10)
    list_frame = Frame(win, bg="#F2DFD7")
    list_frame.pack(fill="both", expand=True, padx=8, pady=6)

    def show_detail_and_pay(tid, d):
        w = Toplevel(win)
        w.title(f"Detail {tid}")
        w.geometry("480x420")
        w.configure(bg="white")

        Label(w, text=f"ID: {tid}", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=(10,0))
        Label(w, text=f"Meja: {d['meja_id']}", bg="white").pack(anchor="w", padx=10)
        Label(w, text=f"Total (di transaksi): Rp {d['total']}", bg="white").pack(anchor="w", padx=10, pady=(0,6))

        items = load_detail_transaksi(tid)
        if not items:
            Label(w, text="Detail tidak ditemukan.", bg="white").pack(pady=10)
        else:
            frame_items = Frame(w, bg="white")
            frame_items.pack(fill="both", expand=True, padx=10)
            Label(frame_items, text="Nama", bg="white", width=20, anchor="w").grid(row=0, column=0)
            Label(frame_items, text="Qty", bg="white", width=6).grid(row=0, column=1)
            Label(frame_items, text="Harga", bg="white", width=10).grid(row=0, column=2)
            Label(frame_items, text="Subtotal", bg="white", width=10).grid(row=0, column=3)

            for i, it in enumerate(items, start=1):
                Label(frame_items, text=it['nama'], bg="white", width=20, anchor="w").grid(row=i, column=0)
                Label(frame_items, text=it['jumlah'], bg="white").grid(row=i, column=1)
                Label(frame_items, text=f"Rp {it['harga']}", bg="white").grid(row=i, column=2)
                Label(frame_items, text=f"Rp {it['subtotal']}", bg="white").grid(row=i, column=3)

        # metode pembayaran
        metode_var = StringVar(value=d.get("metode_pembayaran", "Cash"))
        Label(w, text="Pilih Metode Pembayaran:", bg="white").pack(anchor="w", padx=12, pady=(10,0))
        metode_box = ttk.Combobox(w, textvariable=metode_var, values=["Cash","QR","EDC"], state="readonly")
        metode_box.pack(anchor="w", padx=12)

        def proses():
            set_transaksi_lunas(tid, metode_var.get())
            total_label.config(text=f"Total Penjualan Hari Ini (Lunas): Rp {total_pendapatan_hari_ini()}")
            refresh()
            w.destroy()

        Button(w, text="Proses Pembayaran (Tandai Lunas)", bg="#4CAF50", fg="white", command=proses).pack(pady=12)

    def refresh():
        for w in list_frame.winfo_children():
            w.destroy()

        # load semua transaksi agar kasir bisa kirim ke waiter DAN bisa bayar
        try:
            with open("transaksi.csv", newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except:
            rows = []

        if not rows:
            Label(list_frame, text="Tidak ada pesanan.", bg="#F2DFD7").pack(pady=20)
            return

        for d in rows:
            tid = d["id"]
            status = d["status"]

            box = Frame(list_frame, bg="white", bd=2, relief="groove")
            box.pack(fill="x", pady=6)

            Label(box, text=f"ID: {tid}", bg="white", font=("Arial", 12, "bold")).pack(anchor="w", padx=8)
            Label(box, text=f"Meja: {d['meja_id']}", bg="white").pack(anchor="w", padx=8)
            Label(box, text=f"Total: Rp {d['total']}", bg="white").pack(anchor="w", padx=8)
            Label(box, text=f"Status: {status}", bg="white").pack(anchor="w", padx=8, pady=(0,5))

            btn_frame = Frame(box, bg="white")
            btn_frame.pack(fill="x")

            if status == "Menunggu Konfirmasi":
                Button(btn_frame, text="Konfirmasi & Kirim ke Waiter",
                       command=lambda t=tid: (update_transaksi_status(t, "Disiapkan"), refresh())).pack(side="right", padx=6)

            elif status == "Selesai":
                Button(btn_frame, text="Lihat & Bayar", command=lambda t=tid, x=d: show_detail_and_pay(t, x)).pack(side="right", padx=6)
    refresh()



# ======================================================
# WAITER PAGE
# ======================================================

from tkinter import messagebox

def load_detail_transaksi(order_id):
    """Membaca detail_transaksi.csv untuk order_id tertentu."""
    rows = []
    try:
        with open("detail_transaksi.csv", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("id_transaksi") == order_id:
                    # konversi aman
                    jumlah = int(row.get("jumlah", 0))
                    harga = int(row.get("harga", 0))
                    try:
                        diskon = float(row.get("diskon", 0))
                    except:
                        diskon = 0.0
                    subtotal = int(round(jumlah * harga * (1 - diskon / 100)))
                    rows.append({
                        "nama": row.get("nama", ""),
                        "jumlah": jumlah,
                        "harga": harga,
                        "diskon": diskon,
                        "subtotal": subtotal
                    })
    except FileNotFoundError:
        pass
    return rows

def waiter():
    win = Toplevel(login_window)
    win.title("Halaman Waiter")
    win.geometry("900x600")
    win.configure(bg="#F2DFD7")

    Label(win, text="Pesanan Untuk Disajikan", font=("Arial", 18), bg="#F2DFD7").pack(pady=12)

    control_frame = Frame(win, bg="#F2DFD7")
    control_frame.pack(fill="x", padx=12)

    Label(control_frame, text="Cari Meja:", bg="#F2DFD7").pack(side="left")
    search_var = StringVar()
    search_entry = Entry(control_frame, textvariable=search_var)
    search_entry.pack(side="left", padx=(6,12))

    refresh_btn = Button(control_frame, text="Refresh", command=lambda: refresh())
    refresh_btn.pack(side="right")

    list_frame = Frame(win, bg="#F2DFD7")
    list_frame.pack(fill="both", expand=True, padx=12, pady=8)

    def show_detail_window(order_id, meja_id, total):
        w = Toplevel(win)
        w.title(f"Detail {order_id} - {meja_id}")
        w.geometry("480x400")
        w.configure(bg="white")
        Label(w, text=f"ID: {order_id}", bg="white", font=("Arial", 11, "bold")).pack(anchor='w', padx=10, pady=(8,0))
        Label(w, text=f"Meja: {meja_id}", bg="white").pack(anchor='w', padx=10)
        Label(w, text=f"Total (di transaksi): Rp {total}", bg="white").pack(anchor='w', padx=10, pady=(0,6))

        items = load_detail_transaksi(order_id)
        if not items:
            Label(w, text="Detail tidak ditemukan.", bg="white").pack(padx=10, pady=10)
            return

        frame_items = Frame(w, bg="white")
        frame_items.pack(fill="both", expand=True, padx=10, pady=6)

        # header
        hdr = Frame(frame_items, bg="white")
        hdr.pack(fill="x")
        Label(hdr, text="Nama", bg="white", width=20, anchor='w').grid(row=0, column=0, sticky="w")
        Label(hdr, text="Qty", bg="white", width=6).grid(row=0, column=1)
        Label(hdr, text="Harga", bg="white", width=10).grid(row=0, column=2)
        Label(hdr, text="Subtotal", bg="white", width=12).grid(row=0, column=3)

        sum_sub = 0
        for i, it in enumerate(items, start=1):
            Label(frame_items, text=it['nama'], bg="white", anchor='w', width=20).grid(row=i, column=0, sticky="w")
            Label(frame_items, text=str(it['jumlah']), bg="white", width=6).grid(row=i, column=1)
            Label(frame_items, text=f"Rp {it['harga']}", bg="white", width=10).grid(row=i, column=2)
            Label(frame_items, text=f"Rp {it['subtotal']}", bg="white", width=12).grid(row=i, column=3)
            sum_sub += it['subtotal']

        Label(w, text=f"Subtotal hitung ulang: Rp {sum_sub}", bg="white", font=("Arial", 10, "bold")).pack(anchor='e', padx=12, pady=8)

    def selesai(tid):
        if messagebox.askyesno("Konfirmasi", f"Tandai {tid} sudah diantar?"):
            update_transaksi_status(tid, "Selesai")
            refresh()

    def refresh():
        for w in list_frame.winfo_children():
            w.destroy()

        data = load_transaksi_by_status("Disiapkan")
        # filter by search meja jika ada
        query = search_var.get().strip().lower()
        if not data:
            Label(list_frame, text="Tidak ada pesanan untuk disajikan.", bg="#F2DFD7").pack(pady=20)
            return

        for tid, d in data.items():
            meja_id = d.get("meja_id", "")
            if query and query not in meja_id.lower():
                continue

            box = Frame(list_frame, bg="white", bd=2, relief="groove")
            box.pack(fill="x", pady=6, padx=6)

            top_row = Frame(box, bg="white")
            top_row.pack(fill="x", padx=8, pady=6)
            Label(top_row, text=f"ID: {tid}", font=("Arial", 11, "bold"), bg="white").pack(side="left", anchor='w')
            Label(top_row, text=f"Meja: {meja_id}", bg="white").pack(side="left", padx=12)
            Label(top_row, text=f"Total: Rp {d.get('total')}", bg="white").pack(side="left", padx=12)

            btn_frame = Frame(box, bg="white")
            btn_frame.pack(fill="x", padx=8, pady=(0,8))
            Button(btn_frame, text="Lihat Detail", command=lambda t=tid, m=meja_id, tot=d.get('total'): show_detail_window(t, m, tot)).pack(side="left")
            Button(btn_frame, text="Tandai Sudah Diantar", command=lambda t=tid: selesai(t)).pack(side="right")

    refresh()



# ======================================================
# ADMIN PAGE
# ======================================================

# ======================================================
# ADMIN PAGE
# ======================================================

def admin():
    win = Toplevel(login_window)
    win.title("Halaman Admin")
    win.geometry("900x600")
    win.configure(bg="#F2DFD7")

    Label(win, text="Kelola Menu", font=("Arial", 20, "bold"), bg="#F2DFD7").pack(pady=10)

    # FRAME LIST MENU
    list_frame = Frame(win, bg="#F2DFD7")
    list_frame.pack(fill="both", expand=True, pady=10)

    # FRAME FORM TAMBAH MENU
    form_frame = Frame(win, bg="#E8DCC8", bd=2, relief="ridge")
    form_frame.pack(fill="x", padx=10, pady=10)

    Label(form_frame, text="Tambah Menu Baru", font=("Arial", 14, "bold"), bg="#E8DCC8").grid(row=0, column=0, columnspan=2, pady=5)

    Label(form_frame, text="Nama:", bg="#E8DCC8").grid(row=1, column=0, sticky="w")
    nama_entry = Entry(form_frame, width=30)
    nama_entry.grid(row=1, column=1, pady=3)

    Label(form_frame, text="Harga:", bg="#E8DCC8").grid(row=2, column=0, sticky="w")
    harga_entry = Entry(form_frame, width=30)
    harga_entry.grid(row=2, column=1, pady=3)

    Label(form_frame, text="Stok:", bg="#E8DCC8").grid(row=3, column=0, sticky="w")
    stok_entry = Entry(form_frame, width=30)
    stok_entry.grid(row=3, column=1, pady=3)

    Label(form_frame, text="Foto (path):", bg="#E8DCC8").grid(row=4, column=0, sticky="w")
    foto_entry = Entry(form_frame, width=30)
    foto_entry.grid(row=4, column=1, pady=3)

    def tambah_menu_baru():
        nama = nama_entry.get().strip()
        harga = harga_entry.get().strip()
        stok = stok_entry.get().strip()
        foto = foto_entry.get().strip()

        if not nama or not harga or not stok:
            messagebox.showerror("Error", "Nama, harga, dan stok harus diisi!")
            return

        try:
            harga = int(harga)
            stok = int(stok)
        except:
            messagebox.showerror("Error", "Harga dan stok harus berupa angka!")
            return

        menu = load_menu_data()
        new_id = max([m["id"] for m in menu]) + 1 if menu else 1

        new_item = {
            "id": new_id,
            "nama": nama,
            "harga": harga,
            "stok": stok,
            "foto": foto if foto else "no_image.png"
        }

        menu.append(new_item)
        update_menu(menu)

        refresh_list()
        messagebox.showinfo("Sukses", "Menu berhasil ditambahkan!")

        nama_entry.delete(0, END)
        harga_entry.delete(0, END)
        stok_entry.delete(0, END)
        foto_entry.delete(0, END)

    Button(form_frame, text="Tambah Menu", bg="#4CAF50", fg="white",
           command=tambah_menu_baru).grid(row=5, column=0, columnspan=2, pady=10)

    # ======================================================
    # TABEL LIST MENU
    # ======================================================

    def refresh_list():
        for w in list_frame.winfo_children():
            w.destroy()

        menu_data = load_menu_data()

        Label(list_frame, text="Daftar Menu", font=("Arial", 16, "bold"), bg="#F2DFD7")\
            .pack(pady=8)

        for item in menu_data:
            box = Frame(list_frame, bg="white", bd=2, relief="ridge")
            box.pack(fill="x", padx=10, pady=5)

            Label(box, text=f"{item['nama']} (Rp {item['harga']})", font=("Arial", 12),
                  bg="white").pack(anchor="w", padx=10)

            Label(box, text=f"Stok: {item['stok']}", bg="white").pack(anchor="w", padx=10)

            btn_frame = Frame(box, bg="white")
            btn_frame.pack(anchor="e", pady=5)

            # Tambah stok
            def tambah_stok(id_item):
                menu = load_menu_data()
                for m in menu:
                    if m["id"] == id_item:
                        m["stok"] += 1
                update_menu(menu)
                refresh_list()

            # Kurangi stok
            def kurangi_stok(id_item):
                menu = load_menu_data()
                for m in menu:
                    if m["id"] == id_item and m["stok"] > 0:
                        m["stok"] -= 1
                update_menu(menu)
                refresh_list()

            # Hapus menu
            def hapus_item(id_item):
                if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus menu ini?"):
                    menu = load_menu_data()
                    menu = [m for m in menu if m["id"] != id_item]
                    update_menu(menu)
                    refresh_list()

            Button(btn_frame, text="+ Stok", bg="#4CAF50", fg="white",
                   command=lambda i=item["id"]: tambah_stok(i)).pack(side="left", padx=3)

            Button(btn_frame, text="- Stok", bg="#E67E22", fg="white",
                   command=lambda i=item["id"]: kurangi_stok(i)).pack(side="left", padx=3)

            Button(btn_frame, text="Hapus", bg="#C0392B", fg="white",
                   command=lambda i=item["id"]: hapus_item(i)).pack(side="left", padx=3)

    refresh_list()


# ======================================================
# PEMILIK PAGE
# ======================================================
def load_penjualan_per_hari():
    data = {}
    try:
        with open("transaksi.csv", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tanggal = row.get("tanggal", "").split(" ")[0]  # format YYYY-MM-DD
                if not tanggal:
                    continue
                
                if row.get("status") == "Lunas":
                    total = int(row.get("total", 0))
                    data[tanggal] = data.get(tanggal, 0) + total
    except:
        pass
    return data

def show_graph_penjualan():
    data = load_penjualan_per_hari()

    if not data:
        return

    dates = list(data.keys())
    totals = list(data.values())

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(dates, totals, marker="o")
    ax.set_title("Grafik Pendapatan Harian")
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Pendapatan (Rp)")
    ax.grid(True)

    # buat window tkinter
    graph_win = Toplevel()
    graph_win.title("Grafik Penjualan")
    graph_win.geometry("700x500")

    canvas = FigureCanvasTkAgg(fig, master=graph_win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)



def pemilik():
    win = Toplevel(login_window)
    win.title("Halaman Pemilik")
    win.geometry("800x600")
    win.configure(bg="#F2DFD7")

    Label(win, text="Halaman Pemilik", font=("Arial", 20), bg="#F2DFD7").pack(pady=20)

    Button(
        win,
        text="Lihat Grafik Penjualan Harian",
        font=("Arial", 14),
        command=show_graph_penjualan,
        bg="#4CAF50",
        fg="white"
    ).pack(pady=20)



# ======================================================
# LOGIN ATTEMPT
# ======================================================

def attempt():
    data = login(u_entry.get(), p_entry.get())

    if not data:
        login_status_label.config(text="Username atau password salah!", fg="red")
        return

    login_window.withdraw()

    role = data["role"]

    if role == "pembeli":
        order()
    elif role == "kasir":
        kasir()
    elif role == "waiter":
        waiter()
    elif role == "admin":
        admin()
    elif role == "pemilik":
        pemilik()

# ======================================================
# LOGIN WINDOW UI
# ======================================================

center_frame = Frame(login_window, bg="#F2DFD7")
center_frame.place(relx=0.5, rely=0.5, anchor="center")

Label(center_frame, text="Python Cafe", font=("Ink Free", 32, "bold"), bg="#F2DFD7").pack(pady=(0, 30))

Label(center_frame, text="Username:", font=("Arial", 12), bg="#F2DFD7").pack(anchor="w")
u_entry = Entry(center_frame, font=("Arial", 14), width=30)
u_entry.pack(pady=(0, 10), ipady=4)

Label(center_frame, text="Password:", font=("Arial", 12), bg="#F2DFD7").pack(anchor="w")
p_entry = Entry(center_frame, show="*", font=("Arial", 14), width=30)
p_entry.pack(pady=(0, 20), ipady=4)

loginbutton = Button(center_frame, text="Login", font=("Arial", 14, "bold"), command=attempt, width=15)
loginbutton.pack(pady=10, ipady=5)

login_status_label = Label(center_frame, text="", font=("Arial", 10), bg="#F2DFD7")
login_status_label.pack()

login_window.mainloop()

