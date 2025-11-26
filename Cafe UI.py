from tkinter import *
from PIL import Image, ImageTk
import csv

login_window = Tk()
login_window.geometry("800x600")
login_window.configure(bg="#F2DFD7")

def login(username_input, password_input):
    with open("users.csv", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username_input and row["password"] == password_input:
                return row
    return None

def order(): #halaman pemesanan/order
    import csv
    menu_data = {}
    with open("menu.csv", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            menu_data[int(row["id"])] = row

    stok_kopi = int(menu_data[1]["stok"])
    stok_roti = int(menu_data[2]["stok"])

    order_menu = Toplevel(login_window)
    order_menu.geometry("800x600")
    order_menu.configure(bg="#F2DFD7")

    #label order
    eskopi_gula_aren = Label(order_menu, text=f"Es Kopi Gula Aren\nRp.15.000\nStok: {stok_kopi}")
    roti_bakar_cokelat = Label(order_menu, text=f"Roti Bakar Cokelat\nRp.10.000\nStok: {stok_roti}")

    #gambar2 order
    foto_eskopi = Image.open(menu_data[1]["foto"])
    foto_roti = Image.open(menu_data[2]["foto"])

    foto_eskopi = foto_eskopi.resize((200,150))
    foto_roti = foto_roti.resize((200,150))

    gambar_kopi = ImageTk.PhotoImage(foto_eskopi)
    gambar_roti = ImageTk.PhotoImage(foto_roti)

    tampil_kopi = Label(order_menu, image=gambar_kopi)
    tampil_kopi.image = gambar_kopi
    tampil_roti = Label(order_menu, image=gambar_roti)
    tampil_roti.image = gambar_roti

    def update_csv():
        with open("menu.csv", "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id","nama","kategori","harga","stok","foto"])
            writer.writerow([
                1,
                menu_data[1]["nama"],
                menu_data[1]["kategori"],
                menu_data[1]["harga"],
                menu_data[1]["stok"],
                menu_data[1]["foto"]
            ])
            writer.writerow([
                2,
                menu_data[2]["nama"],
                menu_data[2]["kategori"],
                menu_data[2]["harga"],
                menu_data[2]["stok"],
                menu_data[2]["foto"]
            ])

    def order_kopi():
        nonlocal stok_kopi
        if stok_kopi > 0:
            stok_kopi -= 1
            menu_data[1]["stok"] = stok_kopi
            eskopi_gula_aren.config(text=f"Es Kopi Gula Aren\nRp.15.000\nStok: {stok_kopi}")
            update_csv()
            if stok_kopi == 0:
                button_kopi.config(text="Habis", state="disabled")

    def order_roti():
        nonlocal stok_roti
        if stok_roti > 0:
            stok_roti -= 1
            menu_data[2]["stok"] = stok_roti
            roti_bakar_cokelat.config(text=f"Roti Bakar Cokelat\nRp.10.000\nStok: {stok_roti}")
            update_csv()
            if stok_roti == 0:
                button_roti.config(text="Habis", state="disabled")

    #entry/button order
    button_kopi = Button(order_menu, text="Order", font=("Ink Free", 15), width=10, height=1, command=order_kopi)
    button_roti = Button(order_menu, text="Order", font=("Ink Free", 15), width=10, height=1, command=order_roti)

    if stok_kopi == 0:
        button_kopi.config(text="Habis", state="disabled")
    if stok_roti == 0:
        button_roti.config(text="Habis", state="disabled")

    #atur posisi order
    eskopi_gula_aren.place(x=420, y=150)
    roti_bakar_cokelat.place(x=420, y=350)

    tampil_kopi.place(x=200, y=100)
    tampil_roti.place(x=200, y=300)

    button_kopi.place(x=550, y=130)
    button_roti.place(x=550, y=330)

def pelanggan(): #halaman pembeli/pelanggan
    pelanggan_menu = Toplevel(login_window)   
    pelanggan_menu.configure(bg="#F2DFD7")

    text_kasir = Label(pelanggan_menu, text="Login Pelanggan", font=(15))
    text_nama = Label(pelanggan_menu,text="Nama:")
    text_nomor_meja = Label(pelanggan_menu, text="Nomor Meja")
    user = Entry(pelanggan_menu)
    pw = Entry(pelanggan_menu)

    text_kasir.place(x=600,y=200)
    text_nama.place(x=540, y=240)
    text_nomor_meja.place(x=540, y=310)
    user.config(font=("Ink Free", 15))
    pw.config(font=("Ink Free", 15))

    button = Button(pelanggan_menu, text='Login',font=("Ink Free", 15), width=10, height=1, command=order)
    button.place(x=600, y=380)

    user.place(x=540, y=260)
    pw.place(x=540, y=330)

def kasir(): #halaman kasir
    kasir = Toplevel(login_window)
    kasir.configure(bg="#F2DFD7")   

def waiter(): #halaman waiter
    waiter = Toplevel(login_window)
    waiter.configure(bg="#F2DFD7")      

def admin(): #halaman admin
    admin = Toplevel(login_window)
    admin.configure(bg="#F2DFD7")      

def pemilik(): #halaman pemilik
    pemilik = Toplevel(login_window)   
    pemilik.configure(bg="#F2DFD7")   
    
def attempt():
    data = login(u_entry.get(), p_entry.get())

    role = data["role"]
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

    if not data:
        Label(login_window, text="Login gagal!", fg="red", bg="#F2DFD7").pack()
        return

#label2 login
logintext = Label(login_window, text="Login", font=("Arial", 18), bg="#F2DFD7").pack(pady=10)
usertext = Label(login_window, text="Username:", bg="#F2DFD7")
passtext = Label(login_window, text="Password:", bg="#F2DFD7")

#entry/button login
u_entry = Entry(login_window, font=("Arial", 14))
p_entry = Entry(login_window, show="*", font=("Arial", 14))
loginbutton = Button(login_window, text="Login", font=("Arial", 14), command=attempt)

#tampil/atur posisi login
usertext.pack()
u_entry.pack()
passtext.pack()
p_entry.pack()
loginbutton.pack(pady=15)

login_window.mainloop()
