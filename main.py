from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.window import Window
from textwrap import dedent

from kivymd.app import MDApp
from kivymd.toast import toast as mdtoast
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton

import bcrypt
from db import DB

KV = r"""
MDScreenManager:
    LoginScreen:
    HomeScreen:
    ProductsScreen:
    StockInScreen:
    SaleScreen:
    CustomersScreen:
    TabsScreen:
    CashScreen:

<LoginScreen@MDScreen>:
    name: "login"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(24)
        spacing: dp(16)

        MDLabel:
            text: "Mercadinho"
            font_style: "H4"
            halign: "center"

        MDLabel:
            text: "Login do gerente"
            halign: "center"

        MDTextField:
            id: username
            hint_text: "Usuário"
            mode: "rectangle"

        MDTextField:
            id: password
            hint_text: "Senha"
            password: True
            mode: "rectangle"

        MDRaisedButton:
            text: "Entrar / Registrar (1ª vez)"
            pos_hint: {"center_x": 0.5}
            on_release: app.login_or_register()

<HomeScreen@MDScreen>:
    name: "home"
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Painel"
            right_action_items: [["logout", lambda x: app.logout()]]

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)

            MDLabel:
                id: cash_label
                text: "Caixa: R$ 0,00"
                font_style: "H5"

            MDLabel:
                text: "Ações"
                font_style: "H6"

            MDRaisedButton:
                text: "Produtos / Estoque"
                on_release: app.go("products")

            MDRaisedButton:
                text: "Entrada de Estoque"
                on_release: app.go("stockin")

            MDRaisedButton:
                text: "Venda Rápida"
                on_release: app.go("sale")

            MDRaisedButton:
                text: "Clientes"
                on_release: app.go("customers")

            MDRaisedButton:
                text: "Contas (Fiado)"
                on_release: app.go("tabs")

            MDRaisedButton:
                text: "Retirada / Mov. Caixa"
                on_release: app.go("cash")

<ProductsScreen@MDScreen>:
    name: "products"
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Produtos"
            left_action_items: [["arrow-left", lambda x: app.go("home")]]
            right_action_items: [["plus", lambda x: app.dialog_add_product()]]

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(12)
            spacing: dp(10)

            MDTextField:
                id: prod_q
                hint_text: "Buscar por nome ou SKU"
                mode: "rectangle"
                on_text: app.refresh_products()

            ScrollView:
                MDList:
                    id: prod_list

<StockInScreen@MDScreen>:
    name: "stockin"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Entrada de Estoque"
            left_action_items: [["arrow-left", lambda x: app.go("home")]]

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)

            MDTextField:
                id: stockin_q
                hint_text: "Buscar produto"
                mode: "rectangle"
                on_text: app.refresh_stockin_products()

            ScrollView:
                MDList:
                    id: stockin_list

<SaleScreen@MDScreen>:
    name: "sale"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Venda Rápida"
            left_action_items: [["arrow-left", lambda x: app.go("home")]]

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)

            MDTextField:
                id: sale_q
                hint_text: "Buscar produto p/ adicionar"
                mode: "rectangle"
                on_text: app.refresh_sale_products()

            ScrollView:
                MDList:
                    id: sale_products_list

            MDLabel:
                id: cart_total
                text: "Total: R$ 0,00"
                font_style: "H5"

            MDRaisedButton:
                text: "Finalizar (registrar no controle)"
                on_release: app.finish_sale()

<CustomersScreen@MDScreen>:
    name: "customers"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Clientes"
            left_action_items: [["arrow-left", lambda x: app.go("home")]]
            right_action_items: [["plus", lambda x: app.dialog_add_customer()]]

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(12)
            spacing: dp(10)

            MDTextField:
                id: cust_q
                hint_text: "Buscar cliente"
                mode: "rectangle"
                on_text: app.refresh_customers()

            ScrollView:
                MDList:
                    id: cust_list

<TabsScreen@MDScreen>:
    name: "tabs"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Contas (Fiado)"
            left_action_items: [["arrow-left", lambda x: app.go("home")]]

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(12)
            spacing: dp(10)

            MDLabel:
                text: "Abra/gerencie conta pelo cliente"
                theme_text_color: "Secondary"

            MDTextField:
                id: tab_cust_q
                hint_text: "Buscar cliente para abrir/ver conta"
                mode: "rectangle"
                on_text: app.refresh_tabs_customers()

            ScrollView:
                MDList:
                    id: tab_cust_list

<CashScreen@MDScreen>:
    name: "cash"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: "Movimento do Caixa"
            left_action_items: [["arrow-left", lambda x: app.go("home")]]

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)

            MDLabel:
                id: cash_balance_label
                text: "Saldo: R$ 0,00"
                font_style: "H5"

            MDTextField:
                id: cash_amount
                hint_text: "Valor (ex: 50.00)"
                mode: "rectangle"
                input_filter: "float"

            MDTextField:
                id: cash_note
                hint_text: "Motivo/observação (ex: retirada p/ troco)"
                mode: "rectangle"

            MDRaisedButton:
                text: "Registrar Retirada (Saída)"
                on_release: app.cash_withdraw()
"""

class MercadinhoApp(MDApp):
    def build(self):
        Window.softinput_mode = "below_target"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Teal"

        self.title = "Mercadinho"
        self.db = DB()
        self.db.init_schema()
        self.cart = {}  # product_id -> qty
        return Builder.load_string(KV)

    def toast(self, msg):
        mdtoast(msg)

    def fmt_brl(self, value):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # 🔧 acha o widget que realmente contém o id desejado (não depende de children[])
    def find_widget_with_id(self, root, id_name):
        for w in root.walk(restrict=True):
            if hasattr(w, "ids") and id_name in w.ids:
                return w
        return None

    # ====== Navegação ======
    def go(self, screen):
        self.root.current = screen
        if screen == "home":
            self.refresh_home()
        elif screen == "products":
            self.refresh_products()
        elif screen == "stockin":
            self.refresh_stockin_products()
        elif screen == "sale":
            self.cart.clear()
            self.refresh_sale_products()
            self.update_cart_total()
        elif screen == "customers":
            self.refresh_customers()
        elif screen == "tabs":
            self.refresh_tabs_customers()
        elif screen == "cash":
            self.refresh_cash()

    # ====== Auth ======
    def login_or_register(self):
        s = self.root.get_screen("login")
        username = s.ids.username.text.strip()
        password = s.ids.password.text.strip()
        if not username or not password:
            return self.toast("Preencha usuário e senha.")

        user = self.db.get_user_by_username(username)

        if not self.db.has_any_user():
            pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            self.db.create_user(username, pw_hash)
            self.toast("Gerente criado. Entrando…")
            self.go("home")
            return

        if not user:
            return self.toast("Usuário não encontrado (já existe gerente).")

        ok = bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8"))
        if not ok:
            return self.toast("Senha incorreta.")
        self.go("home")

    def logout(self):
        self.root.current = "login"
        s = self.root.get_screen("login")
        s.ids.password.text = ""

    # ====== Home ======
    def refresh_home(self):
        bal = self.db.cash_balance()
        s = self.root.get_screen("home")
        s.ids.cash_label.text = f"Caixa: {self.fmt_brl(bal)}"
        try:
            self.refresh_cash()
        except Exception:
            pass

    # ====== Produtos ======
    def refresh_products(self, *_):
        s = self.root.get_screen("products")
        q = s.ids.prod_q.text
        items = self.db.search_products(q)

        lst = s.ids.prod_list
        lst.clear_widgets()
        for p in items:
            txt = f"{p['name']}  |  Estoque: {p['stock']}  |  {self.fmt_brl(float(p['price']))}"
            lst.add_widget(TwoLineListItem(
                text=txt,
                secondary_text=f"SKU: {p['sku'] or '-'}  |  Custo: {self.fmt_brl(float(p['cost']))}"
            ))

    def dialog_add_product(self):
        content = Builder.load_string(dedent("""
        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: "520dp"

            ScrollView:
                do_scroll_x: False

                GridLayout:
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(12)
                    spacing: dp(10)

                    MDTextField:
                        id: sku
                        hint_text: "SKU (opcional)"
                        mode: "rectangle"

                    MDTextField:
                        id: name
                        hint_text: "Nome do produto"
                        mode: "rectangle"

                    MDTextField:
                        id: cost
                        hint_text: "Custo (ex: 2.50)"
                        mode: "rectangle"
                        input_filter: "float"

                    MDTextField:
                        id: price
                        hint_text: "Preço venda (ex: 4.00)"
                        mode: "rectangle"
                        input_filter: "float"

                    MDTextField:
                        id: stock
                        hint_text: "Estoque inicial (inteiro)"
                        mode: "rectangle"
                        input_filter: "int"

                    MDTextField:
                        id: min_stock
                        hint_text: "Estoque mínimo (inteiro)"
                        mode: "rectangle"
                        input_filter: "int"
        """))

        form = self.find_widget_with_id(content, "sku")
        if form is None:
            return self.toast("Erro: não achei os campos do produto.")

        def save(*_):
            sku = form.ids.sku.text.strip() or None
            name = form.ids.name.text.strip()
            if not name:
                return self.toast("Nome é obrigatório.")
            cost = float(form.ids.cost.text or 0)
            price = float(form.ids.price.text or 0)
            stock = int(form.ids.stock.text or 0)
            min_stock = int(form.ids.min_stock.text or 0)

            self.db.create_product(sku, name, cost, price, stock, min_stock)
            self.dialog.dismiss()
            self.refresh_products()
            self.toast("Produto criado.")

        self.dialog = MDDialog(
            title="Novo produto",
            type="custom",
            content_cls=content,
            size_hint=(0.95, None),
            height="620dp",
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda *_: self.dialog.dismiss()),
                MDRaisedButton(text="Salvar", on_release=save),
            ],
        )
        self.dialog.open()

    # ====== Entrada de estoque ======
    def refresh_stockin_products(self, *_):
        s = self.root.get_screen("stockin")
        q = s.ids.stockin_q.text
        items = self.db.search_products(q)
        lst = s.ids.stockin_list
        lst.clear_widgets()

        for p in items:
            item = TwoLineListItem(
                text=f"{p['name']} (Estoque: {p['stock']})",
                secondary_text=f"Preço: {self.fmt_brl(float(p['price']))} | Custo: {self.fmt_brl(float(p['cost']))}",
                on_release=lambda x, pid=p["id"]: self.dialog_stock_in(pid)
            )
            lst.add_widget(item)

    def dialog_stock_in(self, product_id):
        p = self.db.one("SELECT * FROM products WHERE id=?;", (product_id,))
        content = Builder.load_string(dedent("""
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(10)
            padding: dp(12)

            MDTextField:
                id: qty
                hint_text: "Quantidade (inteiro)"
                mode: "rectangle"
                input_filter: "int"

            MDTextField:
                id: unit_cost
                hint_text: "Custo unitário (opcional)"
                mode: "rectangle"
                input_filter: "float"

            MDTextField:
                id: note
                hint_text: "Obs (ex: compra no fornecedor X)"
                mode: "rectangle"
        """))

        def apply(*_):
            qty = int(content.ids.qty.text or 0)
            if qty <= 0:
                return self.toast("Quantidade inválida.")
            unit_cost = content.ids.unit_cost.text.strip()
            unit_cost_val = float(unit_cost) if unit_cost else None

            self.db.update_stock(product_id, qty)
            self.db.add_stock_movement(product_id, "IN", qty, unit_cost_val, "PURCHASE",
                                       note=content.ids.note.text.strip() or None)

            if unit_cost_val is not None:
                total = unit_cost_val * qty
                self.db.cash_out("PURCHASE", total, note="Compra/entrada estoque")

            self.dialog.dismiss()
            self.refresh_stockin_products()
            self.refresh_home()
            self.toast("Entrada registrada.")

        self.dialog = MDDialog(
            title=f"Entrada: {p['name']}",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda *_: self.dialog.dismiss()),
                MDRaisedButton(text="Aplicar", on_release=apply),
            ],
        )
        self.dialog.open()

    # ====== Venda rápida ======
    def refresh_sale_products(self, *_):
        s = self.root.get_screen("sale")
        q = s.ids.sale_q.text
        items = self.db.search_products(q)
        lst = s.ids.sale_products_list
        lst.clear_widgets()

        for p in items:
            item = TwoLineListItem(
                text=f"{p['name']} | {self.fmt_brl(float(p['price']))} | Estoque: {p['stock']}",
                secondary_text="Toque para adicionar 1 no carrinho",
                on_release=lambda x, pid=p["id"]: self.add_to_cart(pid, 1)
            )
            lst.add_widget(item)

    def add_to_cart(self, product_id, qty):
        p = self.db.one("SELECT * FROM products WHERE id=?;", (product_id,))
        if p["stock"] <= 0:
            return self.toast("Sem estoque.")
        self.cart[product_id] = self.cart.get(product_id, 0) + qty
        self.update_cart_total()
        self.toast(f"Adicionado: {p['name']} (+{qty})")

    def update_cart_total(self):
        total = 0.0
        for pid, qty in self.cart.items():
            p = self.db.one("SELECT * FROM products WHERE id=?;", (pid,))
            total += float(p["price"]) * qty
        s = self.root.get_screen("sale")
        s.ids.cart_total.text = f"Total: {self.fmt_brl(total)}"

    def finish_sale(self):
        if not self.cart:
            return self.toast("Carrinho vazio.")
        self.dialog_payment_method()

    def dialog_payment_method(self):
        content = Builder.load_string(dedent("""
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(10)
            padding: dp(12)

            MDLabel:
                text: "Forma de pagamento (apenas para controle):"

            MDTextField:
                id: method
                hint_text: "dinheiro / pix / cartao"
                mode: "rectangle"
        """))

        def confirm(*_):
            method = content.ids.method.text.strip().lower() or "dinheiro"
            self.dialog.dismiss()
            self.commit_sale(method)

        self.dialog = MDDialog(
            title="Finalizar venda",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda *_: self.dialog.dismiss()),
                MDRaisedButton(text="Confirmar", on_release=confirm),
            ],
        )
        self.dialog.open()

    def commit_sale(self, method):
        total = 0.0
        items = []
        for pid, qty in self.cart.items():
            p = self.db.one("SELECT * FROM products WHERE id=?;", (pid,))
            if p["stock"] < qty:
                return self.toast(f"Estoque insuficiente: {p['name']}")
            total += float(p["price"]) * qty
            items.append((p, qty))

        sale = self.db.create_sale(total=total, discount=0.0, method=method)

        for p, qty in items:
            self.db.update_stock(p["id"], -qty)
            self.db.add_stock_movement(p["id"], "OUT", qty, None, "SALE", ref_table="sales", ref_id=sale["id"])
            self.db.add_sale_item(sale["id"], p["id"], qty, float(p["price"]), float(p["cost"]))

        self.db.cash_in("SALE", total, note=f"Venda #{sale['id']} ({method})")

        self.cart.clear()
        self.update_cart_total()
        self.refresh_sale_products()
        self.refresh_home()
        self.toast(f"Venda registrada: {self.fmt_brl(total)}")

    # ====== Clientes ======
    def refresh_customers(self, *_):
        s = self.root.get_screen("customers")
        q = s.ids.cust_q.text
        items = self.db.search_customers(q)
        lst = s.ids.cust_list
        lst.clear_widgets()
        for c in items:
            lst.add_widget(TwoLineListItem(
                text=c["name"],
                secondary_text=f"Telefone: {c['phone'] or '-'}"
            ))

    def dialog_add_customer(self):
        content = Builder.load_string(dedent("""
        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: "260dp"

            ScrollView:
                do_scroll_x: False

                GridLayout:
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(12)
                    spacing: dp(10)

                    MDTextField:
                        id: name
                        hint_text: "Nome"
                        mode: "rectangle"

                    MDTextField:
                        id: phone
                        hint_text: "Telefone (opcional)"
                        mode: "rectangle"
        """))

        form = self.find_widget_with_id(content, "name")
        if form is None:
            return self.toast("Erro: não achei os campos do cliente.")

        def save(*_):
            name = form.ids.name.text.strip()
            if not name:
                return self.toast("Nome é obrigatório.")
            phone = form.ids.phone.text.strip() or None

            self.db.create_customer(name, phone)
            self.dialog.dismiss()
            self.refresh_customers()
            self.toast("Cliente criado.")

        self.dialog = MDDialog(
            title="Novo cliente",
            type="custom",
            content_cls=content,
            size_hint=(0.9, None),
            height="340dp",
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda *_: self.dialog.dismiss()),
                MDRaisedButton(text="Salvar", on_release=save),
            ],
        )
        self.dialog.open()

    # ====== Contas (Fiado) ======
    def refresh_tabs_customers(self, *_):
        s = self.root.get_screen("tabs")
        q = s.ids.tab_cust_q.text
        items = self.db.search_customers(q)
        lst = s.ids.tab_cust_list
        lst.clear_widgets()

        for c in items:
            open_tab = self.db.get_open_tab(c["id"])
            status = "ABERTA" if open_tab else "sem conta"
            lst.add_widget(TwoLineListItem(
                text=f"{c['name']} ({status})",
                secondary_text="Toque para abrir/ver conta",
                on_release=lambda x, cid=c["id"]: self.open_or_view_tab(cid)
            ))

    # (resto do seu sistema de fiado/contas pode continuar igual ao que você tinha)
    # Para manter essa resposta num tamanho razoável, eu deixei fiado/caixa como no seu código original.
    # Se você quiser, eu reenvio o arquivo com TUDO (incluindo contas/fiado) re-colado inteiro também.

    def open_or_view_tab(self, customer_id):
        tab = self.db.get_open_tab(customer_id)
        if not tab:
            tab = self.db.open_tab(customer_id)
            self.toast("Conta aberta.")
        self.dialog_manage_tab(tab["id"])

    def dialog_manage_tab(self, tab_id):
        total = self.db.tab_total(tab_id)
        items = self.db.tab_items(tab_id)
        preview = "\n".join([f"- {it['product_name']} x{it['qty']} ({self.fmt_brl(it['unit_price'])})" for it in items[:8]])
        if len(items) > 8:
            preview += "\n..."

        content = Builder.load_string(dedent(f"""
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(10)
            padding: dp(12)

            MDLabel:
                text: "Itens (últimos):"

            MDLabel:
                text: "{preview if preview else '(vazio)'}"
                theme_text_color: "Secondary"

            MDLabel:
                text: "Total: {self.fmt_brl(total)}"
                font_style: "H6"
        """))

        def add_item(*_):
            self.dialog.dismiss()
            self.dialog_add_tab_item(tab_id)

        def close_pay(*_):
            self.dialog.dismiss()
            self.dialog_close_tab(tab_id)

        self.dialog = MDDialog(
            title=f"Conta #{tab_id}",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Voltar", on_release=lambda *_: self.dialog.dismiss()),
                MDFlatButton(text="Adicionar item", on_release=add_item),
                MDRaisedButton(text="Fechar/Pagar", on_release=close_pay),
            ],
        )
        self.dialog.open()

    def dialog_add_tab_item(self, tab_id):
        content = Builder.load_string(dedent("""
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(10)
            padding: dp(12)

            MDTextField:
                id: q
                hint_text: "Buscar produto (pega o primeiro resultado)"
                mode: "rectangle"

            MDTextField:
                id: qty
                hint_text: "Quantidade (inteiro)"
                mode: "rectangle"
                input_filter: "int"
        """))

        def pick_product():
            q = content.ids.q.text.strip()
            prods = self.db.search_products(q)
            if not prods:
                self.toast("Nenhum produto encontrado.")
                return None
            return prods[0]

        def add(*_):
            p = pick_product()
            if not p:
                return
            qty = int(content.ids.qty.text or 0)
            if qty <= 0:
                return self.toast("Quantidade inválida.")
            if p["stock"] < qty:
                return self.toast("Estoque insuficiente.")

            self.db.update_stock(p["id"], -qty)
            self.db.add_stock_movement(p["id"], "OUT", qty, None, "TAB", ref_table="tabs", ref_id=tab_id)
            self.db.add_tab_item(tab_id, p["id"], qty, float(p["price"]))

            self.dialog.dismiss()
            self.refresh_home()
            self.toast("Item adicionado na conta.")
            self.dialog_manage_tab(tab_id)

        self.dialog = MDDialog(
            title="Adicionar na conta",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda *_: self.dialog.dismiss()),
                MDRaisedButton(text="Adicionar", on_release=add),
            ],
        )
        self.dialog.open()

    def dialog_close_tab(self, tab_id):
        total = self.db.tab_total(tab_id)
        content = Builder.load_string(dedent("""
        MDBoxLayout:
            orientation: "vertical"
            spacing: dp(10)
            padding: dp(12)

            MDLabel:
                text: "Forma de pagamento (controle):"

            MDTextField:
                id: method
                hint_text: "dinheiro / pix / cartao"
                mode: "rectangle"
        """))

        def close(*_):
            method = content.ids.method.text.strip().lower() or "dinheiro"
            self.db.close_tab(tab_id)
            self.db.cash_in("TAB_PAYMENT", total, note=f"Conta #{tab_id} ({method})")
            self.dialog.dismiss()
            self.refresh_tabs_customers()
            self.refresh_home()
            self.toast(f"Conta fechada: {self.fmt_brl(total)}")

        self.dialog = MDDialog(
            title=f"Fechar conta #{tab_id} (Total {self.fmt_brl(total)})",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda *_: self.dialog.dismiss()),
                MDRaisedButton(text="Confirmar", on_release=close),
            ],
        )
        self.dialog.open()

    # ====== Caixa ======
    def refresh_cash(self):
        s = self.root.get_screen("cash")
        bal = self.db.cash_balance()
        s.ids.cash_balance_label.text = f"Saldo: {self.fmt_brl(bal)}"

    def cash_withdraw(self):
        s = self.root.get_screen("cash")
        amount_txt = s.ids.cash_amount.text.strip()
        note = s.ids.cash_note.text.strip() or "Retirada"
        if not amount_txt:
            return self.toast("Informe um valor.")
        amount = float(amount_txt)
        if amount <= 0:
            return self.toast("Valor inválido.")
        self.db.cash_out("WITHDRAW", amount, note=note)
        s.ids.cash_amount.text = ""
        s.ids.cash_note.text = ""
        self.refresh_cash()
        self.refresh_home()
        self.toast("Retirada registrada.")

if __name__ == "__main__":
    MercadinhoApp().run()