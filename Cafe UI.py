from tkinter import *
from tkinter import ttk # Import ttk for better widgets like Separator
from PIL import Image, ImageTk
import csv
import datetime
from functools import partial # To pass arguments to command functions

login_window = Tk()
login_window.title("Python Cafe - Login")
login_window.geometry("800x600")
login_window.configure(bg="#F2DFD7")

# --- DATA & LOGIN LOGIC ---

def login(username_input, password_input):
    """Authenticate user from users.csv."""
    with open("users.csv", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username_input and row["password"] == password_input:
                return row
    return None
    
def load_menu_data():
    """Loads all menu items from menu.csv into a dictionary."""
    menu_data = []
    with open("menu.csv", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row['id'] = int(row['id'])
            row['harga'] = int(row['harga'])
            row['stok'] = int(row['stok'])
            menu_data.append(row)
    return menu_data

def update_menu_stok(menu_items):
    """Writes the current state of menu items (with updated stock) back to menu.csv."""
    with open("menu.csv", "w", newline='', encoding="utf-8") as file:
        if not menu_items:
            return
        # Use the keys from the first item as header
        writer = csv.DictWriter(file, fieldnames=menu_items[0].keys())
        writer.writeheader()
        writer.writerows(menu_items)

def save_order(cart):
    """Saves the current cart as a new order in orders.csv."""
    order_id = f"ORD-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    fieldnames = ['order_id', 'item_id', 'nama', 'harga', 'jumlah', 'status']
    
    # Create file and write header if it doesn't exist
    try:
        with open("orders.csv", 'x', newline='', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
    except FileExistsError:
        pass # File already exists

    with open("orders.csv", "a", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        for item in cart:
            item_to_write = item.copy()
            item_to_write['order_id'] = order_id
            item_to_write['status'] = 'Menunggu Konfirmasi'
            writer.writerow(item_to_write)

def load_orders_by_status(status_filter):
    """Loads orders from orders.csv and groups them by order_id, filtered by status."""
    orders = {}
    try:
        with open("orders.csv", newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['status'] == status_filter:
                    order_id = row['order_id']
                    if order_id not in orders:
                        orders[order_id] = []
                    orders[order_id].append(row)
    except FileNotFoundError:
        return {} # Return empty dict if orders.csv doesn't exist yet
    return orders

def update_order_status(target_order_id, new_status):
    """Updates the status of a specific order_id in orders.csv."""
    lines = []
    with open("orders.csv", 'r', newline='', encoding="utf-8") as file:
        reader = csv.reader(file)
        lines = list(reader)
        
    with open("orders.csv", 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(lines[0]) # Write header
        for i in range(1, len(lines)):
            if lines[i][0] == target_order_id:
                lines[i][5] = new_status # Column 5 is 'status'
            writer.writerow(lines[i])

# --- UI WINDOWS ---

def order(): # Halaman pemesanan/order
    order_menu = Toplevel(login_window)
    order_menu.title("Menu Pesanan")
    order_menu.geometry("800x600")
    order_menu.configure(bg="#F2DFD7")

    menu_items = load_menu_data()
    shopping_cart = [] # To store {id, nama, harga, jumlah}

    # Main layout frames
    menu_frame = Frame(order_menu, bg="#F2DFD7")
    menu_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
    
    cart_frame = Frame(order_menu, bg="#FFFFFF", width=250)
    cart_frame.pack(side="right", fill="y")
    cart_frame.pack_propagate(False)

    # --- Cart UI ---
    Label(cart_frame, text="Keranjang", font=("Arial", 16, "bold"), bg="white").pack(pady=10)
    cart_list_frame = Frame(cart_frame, bg="white")
    cart_list_frame.pack(fill="both", expand=True)
    total_price_label = Label(cart_frame, text="Total: Rp 0", font=("Arial", 12, "bold"), bg="white")
    total_price_label.pack(pady=10)

    def update_cart_display():
        # Clear current cart display
        for widget in cart_list_frame.winfo_children():
            widget.destroy()

        total_price = 0
        if not shopping_cart:
            Label(cart_list_frame, text="Keranjang kosong", bg="white").pack(pady=10)
        else:
            for item in shopping_cart:
                cart_item_text = f"{item['nama']} (x{item['jumlah']})"
                Label(cart_list_frame, text=cart_item_text, bg="white", anchor="w").pack(fill="x", padx=10)
                total_price += item['harga'] * item['jumlah']
        
        total_price_label.config(text=f"Total: Rp {total_price:,}")

    def place_order():
        if not shopping_cart:
            return # Don't place empty order
        
        save_order(shopping_cart)
        
        # Clear the cart and update display
        shopping_cart.clear()
        update_cart_display()

        # Show confirmation
        Label(cart_list_frame, text="Pesanan Terkirim!", fg="green", bg="white").pack()
        checkout_button.config(state="disabled")

    checkout_button = Button(cart_frame, text="Buat Pesanan", font=("Arial", 12, "bold"), command=place_order)
    checkout_button.pack(pady=20, padx=10, fill="x")

    # --- Menu UI ---
    def add_to_cart(item_id, label_stok, button_order):
        # Find the item in our list
        for item in menu_items:
            if item['id'] == item_id:
                if item['stok'] > 0:
                    item['stok'] -= 1
                    label_stok.config(text=f"Stok: {item['stok']}")
                    
                    # Add to cart logic
                    found_in_cart = False
                    for cart_item in shopping_cart:
                        if cart_item['item_id'] == item['id']:
                            cart_item['jumlah'] += 1
                            found_in_cart = True
                            break
                    if not found_in_cart:
                        shopping_cart.append({'item_id': item['id'], 'nama': item['nama'], 'harga': item['harga'], 'jumlah': 1})
                    
                    update_cart_display()
                    update_menu_stok(menu_items)

                    if item['stok'] == 0:
                        button_order.config(text="Habis", state="disabled")
                break

    # Dynamically create menu items
    for item in menu_items:
        item_frame = Frame(menu_frame, bg="#F2DFD7")
        item_frame.pack(fill="x", pady=10)

        # Image
        try:
            img = Image.open(item["foto"])
            img = img.resize((150, 120))
            photo_img = ImageTk.PhotoImage(img)
            
            img_label = Label(item_frame, image=photo_img, bg="#F2DFD7")
            img_label.image = photo_img # Keep a reference!
            img_label.pack(side="left", padx=10)
        except FileNotFoundError:
            img_label = Label(item_frame, text="Gambar\ntidak\nditemukan", width=20, height=7, bg="#ECECEC")
            img_label.pack(side="left", padx=10)

        # Details Frame
        details_frame = Frame(item_frame, bg="#F2DFD7")
        details_frame.pack(side="left", padx=10, fill="x", expand=True)

        label_nama = Label(details_frame, text=item['nama'], font=("Arial", 14, "bold"), bg="#F2DFD7", anchor="w")
        label_nama.pack(fill="x")

        label_harga = Label(details_frame, text=f"Rp. {item['harga']:,}", font=("Arial", 12), bg="#F2DFD7", anchor="w")
        label_harga.pack(fill="x")

        label_stok = Label(details_frame, text=f"Stok: {item['stok']}", font=("Arial", 12), bg="#F2DFD7", anchor="w")
        label_stok.pack(fill="x", pady=(0, 5))

        # Order Button
        button_order = Button(item_frame, text="Tambah", font=("Ink Free", 14), width=8)
        # Use partial to pass arguments to the command function
        button_order.config(command=partial(add_to_cart, item['id'], label_stok, button_order))
        
        if item['stok'] == 0:
            button_order.config(text="Habis", state="disabled")
        
        button_order.pack(side="right", padx=20)

        # Separator
        separator = ttk.Separator(menu_frame, orient='horizontal')
        separator.pack(fill='x', pady=5)
    
    update_cart_display() # Initial call to show "Keranjang kosong"

def kasir(): #halaman kasir
    kasir_window = Toplevel(login_window)
    kasir_window.title("Halaman Kasir")
    kasir_window.geometry("800x600")
    kasir_window.configure(bg="#F2DFD7")   
    
    main_frame = Frame(kasir_window, bg="#F2DFD7")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    Label(main_frame, text="Pesanan Masuk", font=("Arial", 18, "bold"), bg="#F2DFD7").pack(pady=(0, 20))

    orders_frame = Frame(main_frame, bg="#F2DFD7")
    orders_frame.pack(fill="both", expand=True)

    def refresh_display():
        # Clear current display
        for widget in orders_frame.winfo_children():
            widget.destroy()

        # Load orders waiting for confirmation
        pending_orders = load_orders_by_status('Menunggu Konfirmasi')

        if not pending_orders:
            Label(orders_frame, text="Tidak ada pesanan baru.", font=("Arial", 14), bg="#F2DFD7").pack(pady=50)
            return

        for order_id, items in pending_orders.items():
            order_frame = Frame(orders_frame, bd=2, relief="groove", bg="white")
            order_frame.pack(fill="x", pady=10, padx=5)

            Label(order_frame, text=f"Order ID: {order_id}", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", padx=10, pady=5)
            
            for item in items:
                item_text = f"- {item['nama']} (x{item['jumlah']})"
                Label(order_frame, text=item_text, font=("Arial", 11), bg="white").pack(anchor="w", padx=20)
            
            confirm_button = Button(order_frame, text="Konfirmasi & Kirim ke Waiter", 
                                    command=lambda o_id=order_id: confirm_and_send(o_id))
            confirm_button.pack(pady=10)

    def confirm_and_send(order_id):
        update_order_status(order_id, 'Disiapkan')
        refresh_display() # Refresh the list after confirming

    refresh_display() # Initial load

def waiter(): #halaman waiter
    waiter_window = Toplevel(login_window)
    waiter_window.title("Halaman Waiter")
    waiter_window.geometry("800x600")
    waiter_window.configure(bg="#F2DFD7")      
    Label(waiter_window, text="Halaman Waiter", font=("Arial", 18), bg="#F2DFD7").pack(pady=50)

def admin(): #halaman admin
    admin_window = Toplevel(login_window)
    admin_window.title("Halaman Admin")
    admin_window.geometry("800x600")
    admin_window.configure(bg="#F2DFD7")      
    Label(admin_window, text="Halaman Admin", font=("Arial", 18), bg="#F2DFD7").pack(pady=50)

def pemilik(): #halaman pemilik
    pemilik_window = Toplevel(login_window)   
    pemilik_window.title("Halaman Pemilik")
    pemilik_window.geometry("800x600")
    pemilik_window.configure(bg="#F2DFD7")   
    Label(pemilik_window, text="Halaman Pemilik", font=("Arial", 18), bg="#F2DFD7").pack(pady=50)

# --- LOGIN ATTEMPT & MAIN WINDOW SETUP ---

def attempt():
    """Handle login attempt and open the corresponding window based on role."""
    data = login(u_entry.get(), p_entry.get())

    if not data:
        # Simple feedback for failed login
        login_status_label.config(text="Username atau password salah!", fg="red")
        return

    # Hide login window and open the correct role window
    login_window.withdraw()
    role = data["role"]
    
    role_actions = {
        "pembeli": order,
        "kasir": kasir,
        "waiter": waiter,
        "admin": admin,
        "pemilik": pemilik
    }
    
    action = role_actions.get(role)
    if action:
        action()

# --- MAIN LOGIN WINDOW LAYOUT ---
# Use a frame for centering content
center_frame = Frame(login_window, bg="#F2DFD7")
center_frame.place(relx=0.5, rely=0.5, anchor="center")

logintext = Label(center_frame, text="Python Cafe", font=("Ink Free", 32, "bold"), bg="#F2DFD7")
logintext.pack(pady=(0, 30))

usertext = Label(center_frame, text="Username:", font=("Arial", 12), bg="#F2DFD7")
usertext.pack(fill="x", padx=10)
u_entry = Entry(center_frame, font=("Arial", 14), width=30)
u_entry.pack(pady=(0, 10), ipady=4)

passtext = Label(center_frame, text="Password:", font=("Arial", 12), bg="#F2DFD7")
passtext.pack(fill="x", padx=10)
p_entry = Entry(center_frame, show="*", font=("Arial", 14), width=30)
p_entry.pack(pady=(0, 20), ipady=4)

loginbutton = Button(center_frame, text="Login", font=("Arial", 14, "bold"), command=attempt, width=15)
loginbutton.pack(pady=10, ipady=5)

login_status_label = Label(center_frame, text="", font=("Arial", 10), bg="#F2DFD7")
login_status_label.pack()

login_window.mainloop()
