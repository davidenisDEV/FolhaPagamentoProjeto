import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from datetime import datetime

class PayrollSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Folha de Pagamento")
        self.file_path = "folha_pagamento.xlsx"
        
        # Valores fictícios das diárias (altere aqui quando tiver os valores reais)
        self.daily_rates = {
            'gerente': 160,
            'atendente': 120,
            'cozinha': 100,  # Valor fictício
            'bar': 200,
            'churrasqueiro': 150,  # Valor fictício
            'seguranca': 130  # Valor fictício
        }
        
        # Funcionários fixos e seus cargos
        self.fixed_employees = {
            'grace': 'atendente',
            'cleria': 'gerente',
            'lucas': 'gerente',
            'emerson': 'atendente',
            'livia': 'atendente',
            'eli': 'atendente',
            'andressa': 'bar',
            'eddie': 'cozinha',
            'amiga eddie': 'cozinha',
            'anchieta': 'churrasqueiro'
        }
        
        # Criar DataFrame vazio ou carregar arquivo existente
        self.columns = ['Data', 'Nome', 'Cargo', 'Dias Trabalhados', 'Adicional', 'Motivo Adicional', 'Valor a Receber']
        if os.path.exists(self.file_path):
            self.df = pd.read_excel(self.file_path)
        else:
            self.df = pd.DataFrame(columns=self.columns)
        
        # Widgets da interface
        self.create_widgets()
        self.update_listbox()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky='nsew')

        # Entradas de dados
        ttk.Label(main_frame, text="Nome:").grid(row=0, column=0, sticky='w')
        self.name_entry = ttk.Entry(main_frame, width=25)
        self.name_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(main_frame, text="Cargo:").grid(row=1, column=0, sticky='w')
        self.role_entry = ttk.Combobox(main_frame, values=list(self.daily_rates.keys()), width=22)
        self.role_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(main_frame, text="Dias Trabalhados:").grid(row=2, column=0, sticky='w')
        self.days_entry = ttk.Entry(main_frame, width=25)
        self.days_entry.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(main_frame, text="Adicional (R$):").grid(row=3, column=0, sticky='w')
        self.additional_entry = ttk.Entry(main_frame, width=25)
        self.additional_entry.grid(row=3, column=1, padx=5, pady=2)

        ttk.Label(main_frame, text="Motivo Adicional:").grid(row=4, column=0, sticky='w')
        self.additional_reason_entry = ttk.Entry(main_frame, width=25)
        self.additional_reason_entry.grid(row=4, column=1, padx=5, pady=2)

        # Botões
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(buttons_frame, text="Adicionar", command=self.add_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Editar", command=self.edit_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Deletar", command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Salvar no Excel", command=self.save_to_excel).pack(side=tk.LEFT, padx=5)

        # Lista de registros
        self.listbox = tk.Listbox(main_frame, width=70, height=10)
        self.listbox.grid(row=6, column=0, columnspan=2, pady=10)
        self.listbox.bind('<<ListboxSelect>>', self.select_entry)

        # Total a ser pago
        self.total_label = ttk.Label(main_frame, text="Total a ser pago: R$0.00", font=('Arial', 10, 'bold'))
        self.total_label.grid(row=7, column=0, columnspan=2, pady=5)

    def calculate_payment(self, role, days, additional):
        base_payment = self.daily_rates[role] * days
        # Adicional a ser adicionado ao valor base de pagamento
        additional_payment = additional 
        return base_payment + additional_payment

    def add_entry(self):
        if self.validate_entries():
            name = self.name_entry.get().lower()
            role = self.role_entry.get()
            days = int(self.days_entry.get())
            additional = float(self.additional_entry.get())
            additional_reason = self.additional_reason_entry.get()
            current_date = datetime.now().strftime("%d/%m/%Y")
            
            # Verifica se é funcionário fixo e ajusta o cargo se necessário
            if name in self.fixed_employees:
                role = self.fixed_employees[name]
            
            payment = self.calculate_payment(role, days, additional)
            
            new_entry = {
                'Data': current_date,
                'Nome': name.title(),
                'Cargo': role,
                'Dias Trabalhados': days,
                'Adicional': additional,
                'Motivo Adicional': additional_reason,
                'Valor a Receber': round(payment, 2)
            }
            self.df = pd.concat([self.df, pd.DataFrame([new_entry])], ignore_index=True)
            self.update_listbox()
            self.clear_entries()
            self.update_total()

    def edit_entry(self):
        selected = self.listbox.curselection()
        if selected and self.validate_entries():
            index = selected[0]
            name = self.name_entry.get().lower()
            role = self.role_entry.get()
            days = int(self.days_entry.get())
            additional = float(self.additional_entry.get())
            additional_reason = self.additional_reason_entry.get()
            current_date = datetime.now().strftime("%d/%m/%Y")
            
            if name in self.fixed_employees:
                role = self.fixed_employees[name]
            
            payment = self.calculate_payment(role, days, additional)
            
            self.df.at[index, 'Data'] = current_date
            self.df.at[index, 'Nome'] = name.title()
            self.df.at[index, 'Cargo'] = role
            self.df.at[index, 'Dias Trabalhados'] = days
            self.df.at[index, 'Adicional'] = additional
            self.df.at[index, 'Motivo Adicional'] = additional_reason
            self.df.at[index, 'Valor a Receber'] = round(payment, 2)
            self.update_listbox()
            self.clear_entries()
            self.update_total()

    def delete_entry(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            self.df = self.df.drop(index).reset_index(drop=True)
            self.update_listbox()
            self.clear_entries()
            self.update_total()

    def save_to_excel(self):
        try:
            self.df.to_excel(self.file_path, index=False)
            messagebox.showinfo("Sucesso", "Dados salvos no Excel com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar dados: {str(e)}")

    def validate_entries(self):
        try:
            int(self.days_entry.get())
            float(self.additional_entry.get())
            return True
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores numéricos!")
            return False

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for _, row in self.df.iterrows():
            self.listbox.insert(tk.END, f"{row['Data']} | {row['Nome']} | {row['Cargo']} | {row['Dias Trabalhados']} dias | R${row['Valor a Receber']}")

    def select_entry(self, event):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            data = self.df.iloc[index]
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, data['Nome'])
            self.role_entry.set(data['Cargo'])
            self.days_entry.delete(0, tk.END)
            self.days_entry.insert(0, str(data['Dias Trabalhados']))
            self.additional_entry.delete(0, tk.END)
            self.additional_entry.insert(0, str(data['Adicional (R$)']))
            self.additional_reason_entry.delete(0, tk.END)
            self.additional_reason_entry.insert(0, data['Motivo Adicional'])

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.role_entry.set('')
        self.days_entry.delete(0, tk.END)
        self.additional_entry.delete(0, tk.END)
        self.additional_reason_entry.delete(0, tk.END)

    def update_total(self):
        total = self.df['Valor a Receber'].sum()
        self.total_label.config(text=f"Total a ser pago: R${total:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PayrollSystem(root)
    root.mainloop()