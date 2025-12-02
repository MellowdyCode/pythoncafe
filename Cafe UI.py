# FULL UPDATED VERSION USING transaksi.csv & detail_transaksi.csv
# (Complete from start to finish — no truncation)

from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import csv
import datetime
from functools import partial

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
    with open("menu.csv", "w", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=menu_items[0].keys())
        writer.writeheader()
        writer.writerows(menu_items)

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

# ======================================================
# ORDER PAGE
# ======================================================

def order():
    win = Toplevel(login_window)
    win.title("Menu Pesanan")
    win.geometry("800x600")
    win.configure(bg="#F2DFD7")

    menu_items = load_menu_data()
    cart = []

    menu_frame = Frame(win, bg="#F2DFD7")
    menu_frame.pack(side="left", fill="both", expand=True)

    cart_frame = Frame(win, bg="white", width=250)
    cart_frame.pack(side="right", fill="y")
    cart_frame.pack_propagate(False)

    Label(cart_frame, text="Keranjang", font=("Arial", 16), bg="white").pack(pady=10)

    # ---------------- KODE DISKON ----------------
    Label(cart_frame, text="Kode Diskon:", bg="white").pack()
    diskon_entry = Entry(cart_frame, font=("Arial", 12), width=15)
    diskon_entry.pack(pady=(0, 10))

    # ---------------- METODE PEMBAYARAN ----------------
    Label(cart_frame, text="Metode Pembayaran:", bg="white").pack()
    metode_var = StringVar()
    metode_box = ttk.Combobox(
        cart_frame,
        textvariable=metode_var,
        values=["Cash", "QR", "EDC"],
        state="readonly",
        width=15
    )
    metode_box.pack(pady=(0, 10))
    metode_box.current(0)

    # ---------------- PILIH MEJA ----------------
    Label(cart_frame, text="Pilih Meja:", bg="white").pack()
    meja_var = StringVar()

    meja_semua = ["Meja 1", "Meja 2", "Meja 3", "Meja 4", "Meja 5"]
    meja_terpakai = get_meja_dipakai()
    meja_bebas = [m for m in meja_semua if m not in meja_terpakai]

    meja_box = ttk.Combobox(
        cart_frame,
        textvariable=meja_var,
        values=meja_bebas,
        state="readonly",
        width=15
    )
    meja_box.pack(pady=(0, 10))

    if meja_bebas:
        meja_box.current(0)
    else:
        meja_box.set("Tidak Ada Meja")
        meja_box.config(state="disabled")

    # ---------------- CART BOX & TOTAL ----------------
    cart_box = Frame(cart_frame, bg="white")
    cart_box.pack(fill="both", expand=True)

    total_label = Label(cart_frame, text="Total: Rp 0", bg="white", font=("Arial", 12))
    total_label.pack(pady=10)

    def refresh_cart():
        for w in cart_box.winfo_children():
            w.destroy()

        total = 0

        if not cart:
            Label(cart_box, text="Keranjang Kosong", bg="white").pack()
        else:
            for c in cart:
                Label(
                    cart_box,
                    text=f"{c['nama']} x{c['jumlah']}",
                    bg="white",
                    anchor='w'
                ).pack(fill="x")
                total += c['harga'] * c['jumlah']

        # ----- DISKON -----
        KODE_DISKON = {
            "CAFE10%": 10,
            "PROMO50": 50,
            "VIP30": 30,
        }

        kode = diskon_entry.get().upper().strip()
        diskon_persen = KODE_DISKON.get(kode, 0)

        if diskon_persen > 0:
            total = total - (total * diskon_persen / 100)

        total_label.config(text=f"Total: Rp {int(total)}")
        return int(total)

    # =====================================================
    #                 CHECKOUT (BENER)
    # =====================================================
    def checkout():
        if not cart:
            return

        # --- Perbaikan Double-booking Meja ---
        meja_terpakai_now = get_meja_dipakai()
        if meja_var.get() in meja_terpakai_now:
            Label(cart_box, text="Meja baru saja dipakai! Pilih meja lain.", fg="red", bg="white").pack()
            return
        # --- End Fix ---

        order_id = f"TRX-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        total_harga = refresh_cart()

        # Kode diskon
        KODE_DISKON = {
            "CAFE10%": 10,
            "PROMO50": 50,
            "VIP30": 30,
        }
        kode = diskon_entry.get().upper().strip()
        diskon_persen = KODE_DISKON.get(kode, 0)

        # Meja & metode
        meja = meja_var.get()
        metode = metode_var.get() if metode_var.get() else "Cash"

        # Simpan transaksi & detail
        save_transaksi(order_id, total_harga, meja, metode)
        save_detail_transaksi(order_id, cart, diskon_persen)

        cart.clear()
        refresh_cart()
        Label(cart_box, text="Pesanan Berhasil!", fg="green", bg="white").pack()

    # ===== TOMBOL CHECKOUT (JANGAN MASUK KE DALAM checkout) =====
    send_btn = Button(cart_frame, text="Buat Pesanan", font=("Arial", 12, "bold"), command=checkout)
    send_btn.pack(pady=20)

    if not meja_bebas:
        send_btn.config(state="disabled")



    # ---------------- MENU ITEM LIST ----------------
    def add_item(item, stok_label, btn):
        if item['stok'] <= 0:
            return

        item['stok'] -= 1
        stok_label.config(text=f"Stok: {item['stok']}")

        existing = next((c for c in cart if c['item_id'] == item['id']), None)
        if existing:
            existing['jumlah'] += 1
        else:
            cart.append({
                'item_id': item['id'],
                'nama': item['nama'],
                'harga': item['harga'],
                'jumlah': 1
            })

        refresh_cart()
        update_menu(menu_items)

        if item['stok'] == 0:
            btn.config(text="Habis", state="disabled")

    for item in menu_items:
        frame = Frame(menu_frame, bg="#F2DFD7")
        frame.pack(fill="x", pady=10)

        try:
            img = Image.open(item['foto']).resize((150, 120))
            img = ImageTk.PhotoImage(img)
            lbl = Label(frame, image=img, bg="#F2DFD7")
            lbl.image = img
            lbl.pack(side="left")
        except:
            Label(frame, text="No Image", width=20, height=7, bg="#ddd").pack(side="left")

        df = Frame(frame, bg="#F2DFD7")
        df.pack(side="left", padx=10)

        Label(df, text=item['nama'], font=("Arial", 14), bg="#F2DFD7").pack(anchor='w')
        Label(df, text=f"Rp {item['harga']}", bg="#F2DFD7").pack(anchor='w')
        stok_label = Label(df, text=f"Stok: {item['stok']}", bg="#F2DFD7")
        stok_label.pack(anchor='w')

        btn = Button(frame, text="Tambah")
        btn.config(command=partial(add_item, item, stok_label, btn))

        if item['stok'] == 0:
            btn.config(text="Habis", state="disabled")

        btn.pack(side="right", padx=20)

        ttk.Separator(menu_frame, orient="horizontal").pack(fill="x", pady=5)

    refresh_cart()


# ======================================================
# KASIR PAGE
# ======================================================

def kasir():
    win = Toplevel(login_window)
    win.title("Halaman Kasir")
    win.geometry("800x600")
    win.configure(bg="#F2DFD7")

    Label(win, text="Pesanan Masuk", font=("Arial", 18), bg="#F2DFD7").pack(pady=20)
    list_frame = Frame(win, bg="#F2DFD7")
    list_frame.pack(fill="both", expand=True)

    def refresh():
        for w in list_frame.winfo_children():
            w.destroy()

        data = load_transaksi_by_status("Menunggu Konfirmasi")

        if not data:
            Label(list_frame, text="Tidak ada pesanan.", bg="#F2DFD7").pack(pady=20)
            return

        for tid, d in data.items():
            box = Frame(list_frame, bg="white", bd=2, relief="groove")
            box.pack(fill="x", pady=10, padx=10)

            Label(
                box,
                text=f"ID Transaksi: {tid}",
                font=("Arial", 12, "bold"),
                bg="white"
            ).pack(anchor="w", padx=10, pady=5)

            Label(
                box,
                text=f"Total: Rp {d['total']}",
                font=("Arial", 11),
                bg="white"
            ).pack(anchor="w", padx=20)

            Button(
                box,
                text="Konfirmasi & Kirim ke Waiter",
                command=lambda x=tid: konfirmasi(x)
            ).pack(pady=10)
    def konfirmasi(tid):
        update_transaksi_status(tid, "Disiapkan")
        refresh()
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

def admin():
    win = Toplevel(login_window)
    win.title("Halaman Admin")
    win.geometry("800x600")
    win.configure(bg="#F2DFD7")

    Label(win, text="Halaman Admin", font=("Arial", 20), bg="#F2DFD7").pack(pady=20)

    Label(win, text="Admin bisa mengelola user dan menu (belum diisi).", bg="#F2DFD7").pack(pady=10)


# ======================================================
# PEMILIK PAGE
# ======================================================

def pemilik():
    win = Toplevel(login_window)
    win.title("Halaman Pemilik")
    win.geometry("800x600")
    win.configure(bg="#F2DFD7")

    Label(win, text="Halaman Pemilik", font=("Arial", 20), bg="#F2DFD7").pack(pady=20)
    Label(win, text="Pemilik bisa melihat semua transaksi (belum diisi).", bg="#F2DFD7").pack(pady=10)


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

