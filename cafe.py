from tkinter import *
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import csv
import qrcode
from io import BytesIO
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ==================== KONFIGURASI WARNA ====================
COLOR_SCHEME = {
    "primary": "#1a1a2e",      # Dark navy
    "secondary": "#16213e",    # Darker blue
    "accent": "#0f3460",       # Deep blue
    "success": "#00d9ff",      # Cyan
    "warning": "#ffc107",      # Yellow
    "danger": "#e94560",       # Pink red
    "light": "#f1f1f1",        # Light gray
    "white": "#ffffff",        # White
    "text_dark": "#1a1a2e",    # Dark text
    "bg_main": "#eaeaea",      # Main background
    "promo": "#ff6b6b"         # Promo red
}

# ==================== FILE DATABASE ====================
ORDERS_FILE = "orders.json"
TRANSACTIONS_FILE = "transactions.json"

# ==================== FUNGSI LOAD/SAVE DATA ====================
def load_orders():
    """Load pesanan dari file JSON"""
    try:
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_orders(orders):
    """Simpan pesanan ke file JSON"""
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(orders, f, indent=2, ensure_ascii=False)

def load_transactions():
    """Load transaksi dari file JSON"""
    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_transactions(transactions):
    """Simpan transaksi ke file JSON"""
    with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, indent=2, ensure_ascii=False)

# ==================== FUNGSI FULLSCREEN ====================
def set_fullscreen(window):
    """Set window ke fullscreen"""
    window.geometry("1920x1080")
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Center window
    x = (screen_width - 1920) // 2
    y = (screen_height - 1080) // 2
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    window.geometry(f"1920x1080+{x}+{y}")
    
def center_window(window, width=1920, height=1080):
    """Center window dengan ukuran minimum 1920x1080"""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Gunakan ukuran minimum atau ukuran layar (yang lebih kecil)
    final_width = min(width, screen_width)
    final_height = min(height, screen_height)
    
    x = (screen_width - final_width) // 2
    y = (screen_height - final_height) // 2
    
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    
    window.geometry(f"{final_width}x{final_height}+{x}+{y}")

# ==================== FUNGSI LOGIN ====================
def login(username_input, password_input):
    """Fungsi untuk memvalidasi login user dari users.csv"""
    try:
        with open("users.csv", newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == username_input and row["password"] == password_input:
                    return row
        return None
    except FileNotFoundError:
        messagebox.showerror("Error", "File users.csv tidak ditemukan!")
        return None

# ==================== FUNGSI LOAD MENU ====================
def load_menu_data():
    """Fungsi untuk membaca data menu dari menu.csv"""
    menu_data = {}
    try:
        with open("menu.csv", newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                menu_data[int(row["id"])] = row
    except FileNotFoundError:
        messagebox.showerror("Error", "File menu.csv tidak ditemukan!")
    return menu_data

# ==================== FUNGSI UPDATE CSV ====================
def update_menu_csv(menu_data):
    """Fungsi untuk menyimpan perubahan menu ke menu.csv"""
    with open("menu.csv", "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "nama", "kategori", "harga", "stok", "foto", "promo"])
        for menu_id in sorted(menu_data.keys()):
            item = menu_data[menu_id]
            promo = item.get("promo", "0")
            writer.writerow([
                menu_id,
                item["nama"],
                item["kategori"],
                item["harga"],
                item["stok"],
                item["foto"],
                promo
            ])

# ==================== FUNGSI INITIALIZE MENU ====================
def initialize_menu():
    """Initialize menu.csv jika kolom promo tidak ada"""
    try:
        menu_data = load_menu_data()
        # Check if promo column exists
        if menu_data:
            first_item = menu_data[list(menu_data.keys())[0]]
            if "promo" not in first_item:
                # Add promo column with default value 0
                for item in menu_data.values():
                    item["promo"] = "0"
                update_menu_csv(menu_data)
                print("Menu CSV updated with promo column")
    except Exception as e:
        print(f"Error initializing menu: {e}")

# ==================== FUNGSI GENERATE QR CODE ====================
def generate_qr(data):
    """Generate QR Code dan return sebagai PhotoImage"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert ke PhotoImage
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    pil_img = Image.open(buffer)
    pil_img = pil_img.resize((250, 250))
    return ImageTk.PhotoImage(pil_img)

# ==================== FUNGSI LOGOUT ====================
def logout(current_window):
    """Fungsi untuk logout dan kembali ke halaman login"""
    result = messagebox.askyesno("Konfirmasi Logout", "Apakah Anda yakin ingin logout?")
    if result:
        current_window.destroy()
        login_window.deiconify()
        u_entry.delete(0, END)
        p_entry.delete(0, END)

# ==================== HALAMAN ORDER (PELANGGAN) ====================
def order(customer_name, table_number):
    """Halaman pemesanan untuk pelanggan"""
    pesanan_list = []
    
    menu_data = load_menu_data()
    
    order_window = Toplevel(login_window)
    order_window.title("Menu Pemesanan")
    set_fullscreen(order_window)
    order_window.configure(bg=COLOR_SCHEME["bg_main"])
    
    # Header dengan gradient effect
    header_frame = Frame(order_window, bg=COLOR_SCHEME["primary"], height=100)
    header_frame.pack(fill=X)
    header_frame.pack_propagate(False)
    
    # Tombol Logout
    btn_logout = Button(header_frame, text="LOGOUT", font=("Arial", 11, "bold"),
                       bg=COLOR_SCHEME["danger"], fg=COLOR_SCHEME["white"],
                       command=lambda: logout(order_window), cursor="hand2",
                       relief=FLAT, bd=0, padx=20, pady=8)
    btn_logout.place(relx=0.97, rely=0.5, anchor=E)
    
    Label(header_frame, text="MENU PEMESANAN", 
          font=("Arial", 28, "bold"), bg=COLOR_SCHEME["primary"], 
          fg=COLOR_SCHEME["success"]).pack(pady=15)
    Label(header_frame, text=f"Pelanggan: {customer_name} | Meja: {table_number}", 
          font=("Arial", 13), bg=COLOR_SCHEME["primary"], 
          fg=COLOR_SCHEME["light"]).pack()
    
    # Main container
    main_container = Frame(order_window, bg=COLOR_SCHEME["bg_main"])
    main_container.pack(fill=BOTH, expand=True)
    
    # Frame kiri untuk menu (75%)
    menu_container = Frame(main_container, bg=COLOR_SCHEME["bg_main"])
    menu_container.pack(side=LEFT, fill=BOTH, expand=True, padx=15, pady=15)
    
    # Frame kanan untuk pesanan (25%)
    pesanan_container = Frame(main_container, bg=COLOR_SCHEME["secondary"], relief=RAISED, bd=3)
    pesanan_container.pack(side=RIGHT, fill=BOTH, padx=(0, 15), pady=15)
    pesanan_container.config(width=400)
    
    # Header pesanan
    pesanan_header = Frame(pesanan_container, bg=COLOR_SCHEME["primary"], height=60)
    pesanan_header.pack(fill=X)
    pesanan_header.pack_propagate(False)
    Label(pesanan_header, text="KERANJANG PESANAN", font=("Arial", 16, "bold"),
          bg=COLOR_SCHEME["primary"], fg=COLOR_SCHEME["success"]).pack(pady=15)
    
    # Canvas untuk list pesanan
    canvas_frame = Frame(pesanan_container, bg=COLOR_SCHEME["secondary"])
    canvas_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    pesanan_canvas = Canvas(canvas_frame, bg=COLOR_SCHEME["secondary"], 
                            highlightthickness=0, bd=0)
    scrollbar = Scrollbar(canvas_frame, orient="vertical", command=pesanan_canvas.yview,
                         bg=COLOR_SCHEME["accent"])
    pesanan_frame = Frame(pesanan_canvas, bg=COLOR_SCHEME["secondary"])
    
    pesanan_frame.bind("<Configure>", 
                       lambda e: pesanan_canvas.configure(scrollregion=pesanan_canvas.bbox("all")))
    
    pesanan_canvas.create_window((0, 0), window=pesanan_frame, anchor="nw")
    pesanan_canvas.configure(yscrollcommand=scrollbar.set)
    
    pesanan_canvas.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)
    
    # Total dan tombol aksi
    bottom_frame = Frame(pesanan_container, bg=COLOR_SCHEME["secondary"])
    bottom_frame.pack(fill=X, padx=10, pady=15)
    
    # Separator
    Frame(bottom_frame, bg=COLOR_SCHEME["success"], height=2).pack(fill=X, pady=10)
    
    total_label = Label(bottom_frame, text="TOTAL: Rp 0", font=("Arial", 18, "bold"),
                       bg=COLOR_SCHEME["secondary"], fg=COLOR_SCHEME["warning"])
    total_label.pack(pady=10)
    
    # Frame untuk tombol
    button_frame = Frame(bottom_frame, bg=COLOR_SCHEME["secondary"])
    button_frame.pack(fill=X, pady=5)
    
    def update_pesanan_display():
        """Update tampilan pesanan"""
        for widget in pesanan_frame.winfo_children():
            widget.destroy()
        
        total = 0
        for i, item in enumerate(pesanan_list):
            item_frame = Frame(pesanan_frame, bg=COLOR_SCHEME["accent"], 
                             relief=RAISED, bd=2)
            item_frame.pack(fill=X, pady=5, padx=5)
            
            Label(item_frame, text=f"{i+1}. {item['nama']}", 
                  font=("Arial", 11, "bold"), bg=COLOR_SCHEME["accent"],
                  fg=COLOR_SCHEME["white"], anchor=W).pack(fill=X, padx=10, pady=5)
            
            harga_normal = int(item['harga_normal'])
            harga_final = int(item['harga'])
            
            if harga_final < harga_normal:
                # Ada diskon
                Label(item_frame, 
                      text=f"Rp {harga_normal:,}", 
                      font=("Arial", 9), bg=COLOR_SCHEME["accent"],
                      fg=COLOR_SCHEME["light"], anchor=W).pack(fill=X, padx=10)
                Label(item_frame, 
                      text=f"Rp {harga_final:,} (PROMO!)", 
                      font=("Arial", 10, "bold"), bg=COLOR_SCHEME["accent"],
                      fg=COLOR_SCHEME["warning"], anchor=W).pack(fill=X, padx=10, pady=(0,5))
            else:
                Label(item_frame, 
                      text=f"Rp {harga_final:,}", 
                      font=("Arial", 10), bg=COLOR_SCHEME["accent"],
                      fg=COLOR_SCHEME["success"], anchor=W).pack(fill=X, padx=10, pady=(0,5))
            
            total += harga_final
        
        if not pesanan_list:
            Label(pesanan_frame, text="Belum ada pesanan", 
                  font=("Arial", 11), bg=COLOR_SCHEME["secondary"],
                  fg=COLOR_SCHEME["light"]).pack(pady=20)
        
        total_label.config(text=f"TOTAL: Rp {total:,}")
    
    def hapus_semua():
        """Hapus semua pesanan"""
        if pesanan_list:
            result = messagebox.askyesno("Konfirmasi", "Hapus semua pesanan?")
            if result:
                pesanan_list.clear()
                update_pesanan_display()
                messagebox.showinfo("Berhasil", "Semua pesanan telah dihapus!")
    
    def kirim_pesanan():
        """Kirim pesanan ke kasir"""
        if not pesanan_list:
            messagebox.showwarning("Peringatan", "Keranjang masih kosong!")
            return
        
        # Hitung total
        total = sum(int(item['harga']) for item in pesanan_list)
        
        # Buat data order
        order_data = {
            "order_id": f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "customer": customer_name,
            "table": table_number,
            "items": pesanan_list.copy(),
            "total": total,
            "status": "pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Simpan ke database
        orders = load_orders()
        orders.append(order_data)
        save_orders(orders)
        
        messagebox.showinfo("Pesanan Dikirim!", 
                           f"Pesanan #{order_data['order_id']}\n" +
                           f"Total: Rp {total:,}\n\n" +
                           "Pesanan Anda telah dikirim ke kasir!\n" +
                           "Silakan menunggu konfirmasi pembayaran.")
        
        order_window.destroy()
        show_payment(order_data)
    
    # Tombol Hapus Semua
    btn_hapus = Button(button_frame, text="HAPUS SEMUA", font=("Arial", 11, "bold"),
                      bg=COLOR_SCHEME["danger"], fg=COLOR_SCHEME["white"],
                      command=hapus_semua, cursor="hand2", relief=FLAT, bd=0, 
                      padx=15, pady=10)
    btn_hapus.pack(side=LEFT, expand=True, fill=X, padx=(0,5))
    
    # Tombol Kirim Pesanan
    btn_kirim = Button(button_frame, text="KIRIM PESANAN", font=("Arial", 11, "bold"),
                      bg=COLOR_SCHEME["success"], fg=COLOR_SCHEME["text_dark"],
                      command=kirim_pesanan, cursor="hand2", relief=FLAT, bd=0,
                      padx=15, pady=10)
    btn_kirim.pack(side=RIGHT, expand=True, fill=X, padx=(5,0))
    
    # Grid menu items (4 kolom)
    def create_menu_card(parent, menu_id, item, row, col):
        """Membuat card menu dengan promo"""
        card_frame = Frame(parent, bg=COLOR_SCHEME["white"], 
                          relief=RAISED, bd=3, cursor="hand2")
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Promo badge
        promo = int(item.get("promo", 0))
        if promo > 0:
            promo_label = Label(card_frame, text=f"-{promo}%", 
                              font=("Arial", 12, "bold"),
                              bg=COLOR_SCHEME["promo"], fg=COLOR_SCHEME["white"],
                              padx=10, pady=5)
            promo_label.place(relx=1, rely=0, anchor=NE)
        
        # Load gambar
        try:
            foto = Image.open(item["foto"])
            foto = foto.resize((180, 135))
            gambar = ImageTk.PhotoImage(foto)
            label_gambar = Label(card_frame, image=gambar, bg=COLOR_SCHEME["white"])
            label_gambar.image = gambar
            label_gambar.pack(pady=10)
        except:
            Label(card_frame, text="No Image", bg=COLOR_SCHEME["white"], 
                  font=("Arial", 10), fg=COLOR_SCHEME["text_dark"], 
                  height=8).pack(pady=10)
        
        # Info menu
        Label(card_frame, text=item["nama"], font=("Arial", 12, "bold"), 
              bg=COLOR_SCHEME["white"], fg=COLOR_SCHEME["text_dark"],
              wraplength=160).pack(pady=5)
        
        # Harga
        harga_normal = int(item["harga"])
        if promo > 0:
            harga_promo = int(harga_normal * (100 - promo) / 100)
            Label(card_frame, text=f"Rp {harga_normal:,}", 
                  font=("Arial", 9, "italic"), bg=COLOR_SCHEME["white"],
                  fg="gray").pack()
            Label(card_frame, text=f"Rp {harga_promo:,}", 
                  font=("Arial", 13, "bold"), bg=COLOR_SCHEME["white"],
                  fg=COLOR_SCHEME["promo"]).pack()
        else:
            Label(card_frame, text=f"Rp {harga_normal:,}", 
                  font=("Arial", 13, "bold"), bg=COLOR_SCHEME["white"],
                  fg=COLOR_SCHEME["accent"]).pack()
        
        stok_label = Label(card_frame, text=f"Stok: {item['stok']}", 
                          font=("Arial", 9), bg=COLOR_SCHEME["white"],
                          fg=COLOR_SCHEME["text_dark"])
        stok_label.pack(pady=5)
        
        def order_item():
            """Order item"""
            stok = int(item["stok"])
            if stok > 0:
                item["stok"] = str(stok - 1)
                stok_label.config(text=f"Stok: {item['stok']}")
                update_menu_csv(menu_data)
                
                # Hitung harga final
                harga_normal = int(item["harga"])
                promo = int(item.get("promo", 0))
                harga_final = int(harga_normal * (100 - promo) / 100) if promo > 0 else harga_normal
                
                pesanan_list.append({
                    'nama': item['nama'],
                    'harga': str(harga_final),
                    'harga_normal': str(harga_normal)
                })
                
                update_pesanan_display()
                
                if int(item["stok"]) == 0:
                    btn_order.config(text="HABIS", state="disabled", 
                                   bg="gray")
            else:
                messagebox.showwarning("Stok Habis", f"{item['nama']} sudah habis!")
        
        # Tombol order
        btn_order = Button(card_frame, text="TAMBAH", font=("Arial", 11, "bold"), 
                          bg=COLOR_SCHEME["success"], fg=COLOR_SCHEME["text_dark"],
                          width=15, command=order_item, cursor="hand2",
                          relief=FLAT, bd=0, pady=8)
        
        if int(item["stok"]) == 0:
            btn_order.config(text="HABIS", state="disabled", bg="gray")
        
        btn_order.pack(pady=10)
    
    # Tampilkan menu dalam grid 4 kolom
    row = 0
    col = 0
    max_cols = 4
    
    menu_ids = sorted(menu_data.keys())
    print(f"Loading {len(menu_ids)} menu items...")  # Debug
    
    for menu_id in menu_ids:
        print(f"Creating card for menu {menu_id}: {menu_data[menu_id]['nama']}")  # Debug
        create_menu_card(menu_container, menu_id, menu_data[menu_id], row, col)
        col += 1
        if col >= max_cols:
            col = 0
            row += 1
    
    # Configure grid
    for i in range(max_cols):
        menu_container.grid_columnconfigure(i, weight=1, uniform="col")
    for i in range(row + 1):
        menu_container.grid_rowconfigure(i, weight=1, uniform="row")
    
    update_pesanan_display()

# ==================== HALAMAN PEMBAYARAN ====================
def show_payment(order_data):
    """Halaman pembayaran dengan QR Code"""
    payment_window = Toplevel(login_window)
    payment_window.title("Pembayaran")
    center_window(payment_window, 1920, 1080)
    payment_window.configure(bg=COLOR_SCHEME["bg_main"])
    
    # Header
    header = Frame(payment_window, bg=COLOR_SCHEME["primary"], height=80)
    header.pack(fill=X)
    header.pack_propagate(False)
    Label(header, text="PEMBAYARAN", font=("Arial", 24, "bold"),
          bg=COLOR_SCHEME["primary"], fg=COLOR_SCHEME["success"]).pack(pady=20)
    
    # Info order
    info_frame = Frame(payment_window, bg=COLOR_SCHEME["bg_main"])
    info_frame.pack(pady=20)
    
    Label(info_frame, text=f"Order ID: {order_data['order_id']}", 
          font=("Arial", 14, "bold"), bg=COLOR_SCHEME["bg_main"]).pack()
    Label(info_frame, text=f"Total: Rp {order_data['total']:,}", 
          font=("Arial", 18, "bold"), bg=COLOR_SCHEME["bg_main"],
          fg=COLOR_SCHEME["danger"]).pack(pady=10)
    
    # QR Code
    qr_frame = Frame(payment_window, bg=COLOR_SCHEME["white"], relief=RAISED, bd=3)
    qr_frame.pack(pady=20)
    
    qr_data = f"PAY:{order_data['order_id']}:Rp{order_data['total']}"
    qr_image = generate_qr(qr_data)
    qr_label = Label(qr_frame, image=qr_image, bg=COLOR_SCHEME["white"])
    qr_label.image = qr_image
    qr_label.pack(padx=20, pady=20)
    
    Label(payment_window, text="Scan QR Code untuk pembayaran", 
          font=("Arial", 12), bg=COLOR_SCHEME["bg_main"]).pack()
    
    Label(payment_window, text="Menunggu konfirmasi dari kasir...", 
          font=("Arial", 10, "italic"), bg=COLOR_SCHEME["bg_main"],
          fg="gray").pack(pady=10)
    
    def check_payment():
        """Check apakah sudah dibayar"""
        transactions = load_transactions()
        for trans in transactions:
            if trans['order_id'] == order_data['order_id'] and trans['status'] == 'paid':
                messagebox.showinfo("Pembayaran Berhasil!", 
                                   "Pembayaran Anda telah dikonfirmasi!\n" +
                                   "Pesanan sedang diproses.")
                payment_window.destroy()
                return
        
        # Check lagi setelah 2 detik
        payment_window.after(2000, check_payment)
    
    check_payment()

# ==================== HALAMAN PELANGGAN ====================
def pelanggan():
    """Halaman login pelanggan"""
    pelanggan_window = Toplevel(login_window)
    pelanggan_window.title("Login Pelanggan")
    center_window(pelanggan_window, 1920, 1080)
    pelanggan_window.configure(bg=COLOR_SCHEME["bg_main"])
    
    header = Frame(pelanggan_window, bg=COLOR_SCHEME["secondary"], height=100)
    header.pack(fill=X)
    header.pack_propagate(False)
    
    btn_logout = Button(header, text="LOGOUT", font=("Arial", 11, "bold"),
                       bg=COLOR_SCHEME["danger"], fg=COLOR_SCHEME["white"],
                       command=lambda: logout(pelanggan_window), cursor="hand2",
                       relief=FLAT, bd=0, padx=20, pady=8)
    btn_logout.place(relx=0.95, rely=0.5, anchor=E)
    
    Label(header, text="LOGIN PELANGGAN", font=("Arial", 24, "bold"), 
          bg=COLOR_SCHEME["secondary"], fg=COLOR_SCHEME["success"]).pack(pady=30)
    
    form_frame = Frame(pelanggan_window, bg=COLOR_SCHEME["bg_main"])
    form_frame.pack(expand=True, pady=40)
    
    Label(form_frame, text="Nama:", font=("Arial", 13, "bold"), 
          bg=COLOR_SCHEME["bg_main"]).pack(anchor=W, padx=50)
    entry_nama = Entry(form_frame, font=("Arial", 14), width=30, bd=2, relief=GROOVE)
    entry_nama.pack(pady=10, padx=50)
    
    Label(form_frame, text="Nomor Meja:", font=("Arial", 13, "bold"), 
          bg=COLOR_SCHEME["bg_main"]).pack(anchor=W, padx=50, pady=(20,0))
    entry_meja = Entry(form_frame, font=("Arial", 14), width=30, bd=2, relief=GROOVE)
    entry_meja.pack(pady=10, padx=50)
    
    def submit():
        nama = entry_nama.get().strip()
        meja = entry_meja.get().strip()
        if nama and meja:
            pelanggan_window.destroy()
            order(nama, meja)
        else:
            messagebox.showwarning("Peringatan", "Mohon isi semua data!")
    
    Button(form_frame, text="MULAI PESAN", font=("Arial", 14, "bold"), 
           bg=COLOR_SCHEME["success"], fg=COLOR_SCHEME["text_dark"],
           width=25, height=2, command=submit, cursor="hand2",
           relief=FLAT, bd=0).pack(pady=40)

# ==================== HALAMAN KASIR ====================
def kasir():
    """Halaman kasir - proses pembayaran"""
    kasir_window = Toplevel(login_window)
    kasir_window.title("Panel Kasir")
    set_fullscreen(kasir_window)
    kasir_window.configure(bg=COLOR_SCHEME["bg_main"])
    
    header = Frame(kasir_window, bg=COLOR_SCHEME["warning"], height=100)
    header.pack(fill=X)
    header.pack_propagate(False)
    
    btn_logout = Button(header, text="LOGOUT", font=("Arial", 11, "bold"),
                       bg=COLOR_SCHEME["danger"], fg=COLOR_SCHEME["white"],
                       command=lambda: logout(kasir_window), cursor="hand2",
                       relief=FLAT, bd=0, padx=20, pady=8)
    btn_logout.place(relx=0.97, rely=0.5, anchor=E)
    
    Label(header, text="PANEL KASIR - PEMBAYARAN", font=("Arial", 28, "bold"), 
          bg=COLOR_SCHEME["warning"], fg=COLOR_SCHEME["text_dark"]).pack(pady=30)
    
    # Container
    container = Frame(kasir_window, bg=COLOR_SCHEME["bg_main"])
    container.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    # Tabel pesanan
    columns = ("Order ID", "Pelanggan", "Meja", "Total", "Status", "Waktu")
    tree = ttk.Treeview(container, columns=columns, show="headings", height=20)
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor=CENTER)
    
    tree.pack(fill=BOTH, expand=True)
    
    def refresh_orders():
        """Refresh daftar pesanan"""
        tree.delete(*tree.get_children())
        orders = load_orders()
        
        for order in orders:
            tree.insert("", END, values=(
                order['order_id'],
                order['customer'],
                order['table'],
                f"Rp {order['total']:,}",
                order['status'].upper(),
                order['timestamp']
            ))
    
    def konfirmasi_bayar():
        """Konfirmasi pembayaran"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih pesanan terlebih dahulu!")
            return
        
        item = tree.item(selected[0])
        order_id = item['values'][0]
        
        orders = load_orders()
        for order in orders:
            if order['order_id'] == order_id:
                if order['status'] == 'paid':
                    messagebox.showinfo("Info", "Pesanan sudah dibayar!")
                    return
                
                result = messagebox.askyesno("Konfirmasi", 
                                            f"Konfirmasi pembayaran?\n\n" +
                                            f"Order: {order_id}\n" +
                                            f"Total: Rp {order['total']:,}")
                if result:
                    order['status'] = 'paid'
                    save_orders(orders)
                    
                    # Simpan transaksi
                    transactions = load_transactions()
                    transactions.append(order)
                    save_transactions(transactions)
                    
                    messagebox.showinfo("Berhasil", "Pembayaran dikonfirmasi!\n" +
                                                "Pesanan diteruskan ke waiter.")
                    refresh_orders()
                break
    
    btn_frame = Frame(container, bg=COLOR_SCHEME["bg_main"])
    btn_frame.pack(fill=X, pady=20)
    
    Button(btn_frame, text="REFRESH", font=("Arial", 13, "bold"),
           bg=COLOR_SCHEME["accent"], fg=COLOR_SCHEME["white"],
           command=refresh_orders, cursor="hand2", relief=FLAT,
           padx=30, pady=12).pack(side=LEFT, padx=10)
    
    Button(btn_frame, text="KONFIRMASI BAYAR", font=("Arial", 13, "bold"),
           bg=COLOR_SCHEME["success"], fg=COLOR_SCHEME["text_dark"],
           command=konfirmasi_bayar, cursor="hand2", relief=FLAT,
           padx=30, pady=12).pack(side=LEFT, padx=10)
    
    refresh_orders()
    kasir_window.after(3000, refresh_orders)

# ==================== HALAMAN WAITER ====================
def waiter():
    """Halaman waiter - kirim makanan"""
    waiter_window = Toplevel(login_window)
    waiter_window.title("Panel Waiter")
    set_fullscreen(waiter_window)
    waiter_window.configure(bg=COLOR_SCHEME["bg_main"])
    
    header = Frame(waiter_window, bg=COLOR_SCHEME["success"], height=100)
    header.pack(fill=X)
    header.pack_propagate(False)
    
    btn_logout = Button(header, text="LOGOUT", font=("Arial", 11, "bold"),
                       bg=COLOR_SCHEME["danger"], fg=COLOR_SCHEME["white"],
                       command=lambda: logout(waiter_window), cursor="hand2",
                       relief=FLAT, bd=0, padx=20, pady=8)
    btn_logout.place(relx=0.97, rely=0.5, anchor=E)
    
    Label(header, text="PANEL WAITER - PENGIRIMAN", font=("Arial", 28, "bold"), 
          bg=COLOR_SCHEME["success"], fg=COLOR_SCHEME["text_dark"]).pack(pady=30)
    
    container = Frame(waiter_window, bg=COLOR_SCHEME["bg_main"])
    container.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    Label(container, text="PESANAN SIAP KIRIM", font=("Arial", 16, "bold"),
          bg=COLOR_SCHEME["bg_main"]).pack(pady=10)
    
    # Tabel pesanan yang sudah dibayar
    columns = ("Order ID", "Pelanggan", "Meja", "Items", "Status", "Waktu")
    tree = ttk.Treeview(container, columns=columns, show="headings", height=20)
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=180, anchor=CENTER)
    
    tree.pack(fill=BOTH, expand=True, pady=10)
    
    def refresh_orders():
        """Refresh pesanan yang sudah dibayar"""
        tree.delete(*tree.get_children())
        orders = load_orders()
        
        for order in orders:
            if order['status'] == 'paid':
                items_str = ", ".join([item['nama'] for item in order['items'][:3]])
                if len(order['items']) > 3:
                    items_str += "..."
                
                tree.insert("", END, values=(
                    order['order_id'],
                    order['customer'],
                    order['table'],
                    items_str,
                    "SIAP KIRIM",
                    order['timestamp']
                ))
    
    def kirim_pesanan():
        """Kirim pesanan ke pelanggan"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih pesanan terlebih dahulu!")
            return
        
        item = tree.item(selected[0])
        order_id = item['values'][0]
        customer = item['values'][1]
        table = item['values'][2]
        
        result = messagebox.askyesno("Konfirmasi Pengiriman",
                                    f"Kirim pesanan ke:\n\n" +
                                    f"Pelanggan: {customer}\n" +
                                    f"Meja: {table}\n" +
                                    f"Order: {order_id}")
        if result:
            orders = load_orders()
            for order in orders:
                if order['order_id'] == order_id:
                    order['status'] = 'delivered'
                    save_orders(orders)
                    break
            
            messagebox.showinfo("Pesanan Terkirim!", 
                              f"Pesanan #{order_id}\n" +
                              f"telah dikirim ke Meja {table}!\n\n" +
                              "Selamat menikmati!")
            refresh_orders()
    
    btn_frame = Frame(container, bg=COLOR_SCHEME["bg_main"])
    btn_frame.pack(fill=X, pady=20)
    
    Button(btn_frame, text="REFRESH", font=("Arial", 13, "bold"),
           bg=COLOR_SCHEME["accent"], fg=COLOR_SCHEME["white"],
           command=refresh_orders, cursor="hand2", relief=FLAT,
           padx=30, pady=12).pack(side=LEFT, padx=10)
    
    Button(btn_frame, text="KIRIM PESANAN", font=("Arial", 13, "bold"),
           bg=COLOR_SCHEME["warning"], fg=COLOR_SCHEME["text_dark"],
           command=kirim_pesanan, cursor="hand2", relief=FLAT,
           padx=30, pady=12).pack(side=LEFT, padx=10)
    
    refresh_orders()
    waiter_window.after(3000, refresh_orders)

# ==================== HALAMAN ADMIN ====================
def admin():
    """Halaman admin - kelola menu dan promo"""
    admin_window = Toplevel(login_window)
    admin_window.title("Panel Admin")
    set_fullscreen(admin_window)
    admin_window.configure(bg=COLOR_SCHEME["bg_main"])
    
    header = Frame(admin_window, bg=COLOR_SCHEME["primary"], height=100)
    header.pack(fill=X)
    header.pack_propagate(False)
    
    btn_logout = Button(header, text="LOGOUT", font=("Arial", 11, "bold"),
                       bg=COLOR_SCHEME["danger"], fg=COLOR_SCHEME["white"],
                       command=lambda: logout(admin_window), cursor="hand2",
                       relief=FLAT, bd=0, padx=20, pady=8)
    btn_logout.place(relx=0.97, rely=0.5, anchor=E)
    
    Label(header, text="PANEL ADMIN - KELOLA MENU", font=("Arial", 28, "bold"), 
          bg=COLOR_SCHEME["primary"], fg=COLOR_SCHEME["success"]).pack(pady=30)
    
    container = Frame(admin_window, bg=COLOR_SCHEME["bg_main"])
    container.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    columns = ("ID", "Nama", "Kategori", "Harga", "Stok", "Promo")
    tree = ttk.Treeview(container, columns=columns, show="headings", height=20)
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor=CENTER)
    
    tree.pack(fill=BOTH, expand=True, pady=10)
    
    def refresh_menu():
        """Refresh tabel menu"""
        tree.delete(*tree.get_children())
        menu_data = load_menu_data()
        
        for menu_id in sorted(menu_data.keys()):
            item = menu_data[menu_id]
            promo = item.get("promo", "0")
            tree.insert("", END, values=(
                menu_id, item["nama"], item["kategori"],
                f"Rp {int(item['harga']):,}", item["stok"],
                f"{promo}%"
            ))
    
    def update_promo():
        """Update promo menu"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih menu terlebih dahulu!")
            return
        
        item = tree.item(selected[0])
        menu_id = item['values'][0]
        nama = item['values'][1]
        
        promo_window = Toplevel(admin_window)
        promo_window.title("Update Promo")
        promo_window.geometry("300x200")
        promo_window.configure(bg=COLOR_SCHEME["bg_main"])
        
        Label(promo_window, text=f"Update Promo\n{nama}", 
              font=("Arial", 12, "bold"), bg=COLOR_SCHEME["bg_main"]).pack(pady=20)
        
        Label(promo_window, text="Diskon (%):", bg=COLOR_SCHEME["bg_main"]).pack()
        entry_promo = Entry(promo_window, font=("Arial", 14), width=15)
        entry_promo.pack(pady=10)
        
        def save_promo():
            try:
                promo_val = int(entry_promo.get())
                if 0 <= promo_val <= 100:
                    menu_data = load_menu_data()
                    menu_data[menu_id]["promo"] = str(promo_val)
                    update_menu_csv(menu_data)
                    messagebox.showinfo("Berhasil", "Promo berhasil diupdate!")
                    promo_window.destroy()
                    refresh_menu()
                else:
                    messagebox.showerror("Error", "Promo harus 0-100%")
            except:
                messagebox.showerror("Error", "Masukkan angka yang valid!")
        
        Button(promo_window, text="SIMPAN", font=("Arial", 12, "bold"),
               bg=COLOR_SCHEME["success"], fg=COLOR_SCHEME["text_dark"],
               command=save_promo, cursor="hand2").pack(pady=10)
    
    btn_frame = Frame(container, bg=COLOR_SCHEME["bg_main"])
    btn_frame.pack(fill=X, pady=20)
    
    Button(btn_frame, text="REFRESH", font=("Arial", 13, "bold"),
           bg=COLOR_SCHEME["accent"], fg=COLOR_SCHEME["white"],
           command=refresh_menu, cursor="hand2", relief=FLAT,
           padx=30, pady=12).pack(side=LEFT, padx=10)
    
    Button(btn_frame, text="UPDATE PROMO", font=("Arial", 13, "bold"),
           bg=COLOR_SCHEME["promo"], fg=COLOR_SCHEME["white"],
           command=update_promo, cursor="hand2", relief=FLAT,
           padx=30, pady=12).pack(side=LEFT, padx=10)
    
    refresh_menu()

# ==================== HALAMAN PEMILIK ====================
def pemilik():
    """Halaman pemilik - laporan"""
    pemilik_window = Toplevel(login_window)
    pemilik_window.title("Panel Pemilik")
    set_fullscreen(pemilik_window)
    pemilik_window.configure(bg=COLOR_SCHEME["bg_main"])
    
    header = Frame(pemilik_window, bg=COLOR_SCHEME["danger"], height=100)
    header.pack(fill=X)
    header.pack_propagate(False)
    
    btn_logout = Button(header, text="LOGOUT", font=("Arial", 11, "bold"),
                       bg=COLOR_SCHEME["white"], fg=COLOR_SCHEME["danger"],
                       command=lambda: logout(pemilik_window), cursor="hand2",
                       relief=FLAT, bd=0, padx=20, pady=8)
    btn_logout.place(relx=0.97, rely=0.5, anchor=E)
    
    Label(header, text="PANEL PEMILIK - LAPORAN", font=("Arial", 28, "bold"), 
          bg=COLOR_SCHEME["danger"], fg=COLOR_SCHEME["white"]).pack(pady=30)
    
    container = Frame(pemilik_window, bg=COLOR_SCHEME["bg_main"])
    container.pack(fill=BOTH, expand=True, padx=20, pady=20)
    
    # Dashboard
    dashboard = Frame(container, bg=COLOR_SCHEME["bg_main"])
    dashboard.pack(fill=X, pady=20)
    
    transactions = load_transactions()
    total_revenue = sum(t['total'] for t in transactions)
    total_orders = len(transactions)
    
    # Cards
    card_frame = Frame(dashboard, bg=COLOR_SCHEME["bg_main"])
    card_frame.pack(fill=X)
    
    # Card 1
    card1 = Frame(card_frame, bg=COLOR_SCHEME["success"], relief=RAISED, bd=3)
    card1.pack(side=LEFT, expand=True, fill=BOTH, padx=10, ipadx=30, ipady=20)
    Label(card1, text="TOTAL PENDAPATAN", font=("Arial", 14, "bold"),
          bg=COLOR_SCHEME["success"], fg=COLOR_SCHEME["text_dark"]).pack(pady=5)
    Label(card1, text=f"Rp {total_revenue:,}", font=("Arial", 24, "bold"),
          bg=COLOR_SCHEME["success"], fg=COLOR_SCHEME["white"]).pack(pady=5)
    
    # Card 2
    card2 = Frame(card_frame, bg=COLOR_SCHEME["warning"], relief=RAISED, bd=3)
    card2.pack(side=LEFT, expand=True, fill=BOTH, padx=10, ipadx=30, ipady=20)
    Label(card2, text="TOTAL PESANAN", font=("Arial", 14, "bold"),
          bg=COLOR_SCHEME["warning"], fg=COLOR_SCHEME["text_dark"]).pack(pady=5)
    Label(card2, text=str(total_orders), font=("Arial", 24, "bold"),
          bg=COLOR_SCHEME["warning"], fg=COLOR_SCHEME["white"]).pack(pady=5)
    
    # Tabel transaksi
    Label(container, text="RIWAYAT TRANSAKSI", font=("Arial", 16, "bold"),
          bg=COLOR_SCHEME["bg_main"]).pack(pady=20)
    
    columns = ("Order ID", "Pelanggan", "Meja", "Total", "Waktu")
    tree = ttk.Treeview(container, columns=columns, show="headings", height=15)
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=180, anchor=CENTER)
    
    tree.pack(fill=BOTH, expand=True)
    
    for trans in transactions:
        tree.insert("", END, values=(
            trans['order_id'],
            trans['customer'],
            trans['table'],
            f"Rp {trans['total']:,}",
            trans['timestamp']
        ))

# ==================== FUNGSI ATTEMPT LOGIN ====================
def attempt():
    """Proses login"""
    username = u_entry.get().strip()
    password = p_entry.get().strip()
    
    if not username or not password:
        messagebox.showwarning("Peringatan", "Username dan password harus diisi!")
        return
    
    data = login(username, password)
    
    if data:
        role = data["role"]
        login_window.withdraw()
        
        if role == "pembeli":
            pelanggan()
        elif role == "kasir":
            kasir()
        elif role == "waiter":
            waiter()
        elif role == "admin":
            admin()
        elif role == "pemilik":
            pemilik()
    else:
        messagebox.showerror("Login Gagal", "Username atau password salah!")

# ==================== WINDOW LOGIN UTAMA ====================
login_window = Tk()
login_window.title("Sistem Cafe Management")
center_window(login_window, 1920, 1080)
login_window.configure(bg=COLOR_SCHEME["bg_main"])

# Initialize menu CSV (tambah kolom promo jika belum ada)
initialize_menu()

# Header
header_frame = Frame(login_window, bg=COLOR_SCHEME["primary"], height=150)
header_frame.pack(fill=X)
header_frame.pack_propagate(False)

Label(header_frame, text="CAFE MANAGEMENT", font=("Arial", 32, "bold"), 
      bg=COLOR_SCHEME["primary"], fg=COLOR_SCHEME["success"]).pack(pady=25)
Label(header_frame, text="Sistem Login", font=("Arial", 16), 
      bg=COLOR_SCHEME["primary"], fg=COLOR_SCHEME["light"]).pack()

# Form
form_frame = Frame(login_window, bg=COLOR_SCHEME["bg_main"])
form_frame.pack(expand=True, pady=50)

Label(form_frame, text="Username:", font=("Arial", 13, "bold"), 
      bg=COLOR_SCHEME["bg_main"], fg=COLOR_SCHEME["text_dark"]).pack(anchor=W, padx=60)
u_entry = Entry(form_frame, font=("Arial", 14), width=30, bd=2, relief=GROOVE)
u_entry.pack(pady=10, padx=60)

Label(form_frame, text="Password:", font=("Arial", 13, "bold"), 
      bg=COLOR_SCHEME["bg_main"], fg=COLOR_SCHEME["text_dark"]).pack(anchor=W, padx=60, pady=(20,0))
p_entry = Entry(form_frame, show="●", font=("Arial", 14), width=30, bd=2, relief=GROOVE)
p_entry.pack(pady=10, padx=60)

p_entry.bind('<Return>', lambda e: attempt())

Button(form_frame, text="LOGIN", font=("Arial", 15, "bold"), 
       bg=COLOR_SCHEME["success"], fg=COLOR_SCHEME["text_dark"],
       width=25, height=2, command=attempt, cursor="hand2", 
       relief=FLAT, bd=0).pack(pady=50)

Label(login_window, text="© 2024 Cafe Management System", 
      font=("Arial", 10), bg=COLOR_SCHEME["bg_main"], 
      fg=COLOR_SCHEME["text_dark"]).pack(side=BOTTOM, pady=15)

login_window.mainloop()