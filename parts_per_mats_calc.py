import sys
import os
import customtkinter as ctk
from tkinter import StringVar, messagebox, Toplevel, Canvas
import json
import webbrowser
from PIL import Image, ImageDraw

class MaterialUsageCalculator(ctk.CTk):
    on_top = "Always on Top"
    theme = "Theme"
    sheet_length = "Sheet Length"
    sheet_width = "Sheet Width"
    part_length = "Part Length"
    part_width = "Part Width"
    gap_size = "Gap Size"
    def __init__(self):
        super().__init__()
        self.model_window = None
        self.default_settings = {
            self.on_top: True,
            self.theme: "Dark",
            self.sheet_length: "",
            self.sheet_width: "",
            self.part_length: "",
            self.part_width: "",
            self.gap_size: ""
        }

        self.settings = self.load_last_used_settings()
        self.title("Material Usage Calculator")
        self.geometry("400x600")
        self.resizable(False, False)
        self.attributes("-topmost", self.settings[self.on_top])

        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(pady=10)

        self.always_on_top_var = ctk.BooleanVar()
        self.always_on_top_var.set(self.settings[self.on_top])
        self.always_on_top_toggle = ctk.CTkSwitch(self.top_frame, text=self.on_top, variable=self.always_on_top_var, command=self.toggle_always_on_top)
        self.always_on_top_toggle.pack(side="left", padx=10)

        self.theme_var = ctk.StringVar(value=self.settings[self.theme])
        self.theme_toggle = ctk.CTkSegmentedButton(self.top_frame, values=["Light", "Dark"], variable=self.theme_var, command=self.toggle_theme)
        self.theme_toggle.pack(side="right", padx=10)
        ctk.set_appearance_mode(self.settings[self.theme].lower())

        self.sheet_size_group = ctk.CTkFrame(self)
        self.sheet_size_group.pack(pady=10, padx=10, fill="x")

        self.sheet_label = ctk.CTkLabel(self.sheet_size_group, text="Material Size:")
        self.sheet_label.pack(anchor="w")

        self.sheet_length_label = ctk.CTkLabel(self.sheet_size_group, text="Length:")
        self.sheet_length_label.pack(side="left", padx=5)
        self.sheet_length_entry = ctk.CTkEntry(self.sheet_size_group)
        self.sheet_length_entry.pack(side="left", padx=5)
        self.sheet_length_entry.insert(0, self.settings[self.sheet_length])

        self.sheet_width_label = ctk.CTkLabel(self.sheet_size_group, text="Width:")
        self.sheet_width_label.pack(side="left", padx=5)
        self.sheet_width_entry = ctk.CTkEntry(self.sheet_size_group)
        self.sheet_width_entry.pack(side="left", padx=5)
        self.sheet_width_entry.insert(0, self.settings[self.sheet_width])

        self.part_size_group = ctk.CTkFrame(self)
        self.part_size_group.pack(pady=10, padx=10, fill="x")

        self.part_label = ctk.CTkLabel(self.part_size_group, text="Part Size:")
        self.part_label.pack(anchor="w")

        self.part_length_label = ctk.CTkLabel(self.part_size_group, text="Length:")
        self.part_length_label.pack(side="left", padx=5)
        self.part_length_entry = ctk.CTkEntry(self.part_size_group)
        self.part_length_entry.pack(side="left", padx=5)
        self.part_length_entry.insert(0, self.settings[self.part_length])

        self.part_width_label = ctk.CTkLabel(self.part_size_group, text="Width:")
        self.part_width_label.pack(side="left", padx=5)
        self.part_width_entry = ctk.CTkEntry(self.part_size_group)
        self.part_width_entry.pack(side="left", padx=5)
        self.part_width_entry.insert(0, self.settings[self.part_width])

        self.gap_group = ctk.CTkFrame(self)
        self.gap_group.pack(pady=10, padx=10, fill="x")

        self.gap_label = ctk.CTkLabel(self.gap_group, text="Gap Between Parts:")
        self.gap_label.pack(anchor="w")

        self.gap_size_label = ctk.CTkLabel(self.gap_group, text="Gap Size:")
        self.gap_size_label.pack(side="left", padx=5)
        self.gap_size_entry = ctk.CTkEntry(self.gap_group)
        self.gap_size_entry.pack(side="left", padx=5)
        self.gap_size_entry.insert(0, self.settings[self.gap_size])

        self.calculate_button = ctk.CTkButton(self, text="Calculate", command=self.calculate_and_save)
        self.calculate_button.pack(pady=20)

        self.view_model_button = ctk.CTkButton(self, text="View Model", command=self.open_model_window)
        self.view_model_button.pack(pady=10)

        self.view_html_report_button = ctk.CTkButton(self, text="View HTML Report", command=self.generate_html_report)
        self.view_html_report_button.pack(pady=10)

        self.result_label = ctk.CTkLabel(self, text="Maximum Parts: N/A")
        self.result_label.pack(pady=10)

        self.material_usage_label = ctk.CTkLabel(self, text="Material per Part: N/A")
        self.material_usage_label.pack(pady=10)

        self.history_file = "material_usage_history.json"

    def toggle_always_on_top(self):
        self.attributes("-topmost", self.always_on_top_var.get())
        self.save_last_used_settings()

    def toggle_theme(self, selected_theme):
        ctk.set_appearance_mode(selected_theme.lower())
        self.save_last_used_settings()

    def calculate_and_save(self):
        try:
            sheet_length = float(self.sheet_length_entry.get())
            sheet_width = float(self.sheet_width_entry.get())
            part_length = float(self.part_length_entry.get())
            part_width = float(self.part_width_entry.get())
            gap_size = float(self.gap_size_entry.get())

            parts_in_length1 = int(sheet_length // (part_length + gap_size))
            parts_in_width1 = int(sheet_width // (part_width + gap_size))
            total_parts1 = parts_in_length1 * parts_in_width1

            parts_in_length2 = int(sheet_length // (part_width + gap_size))
            parts_in_width2 = int(sheet_width // (part_length + gap_size))
            total_parts2 = parts_in_length2 * parts_in_width2

            if total_parts2 > total_parts1:
                total_parts = total_parts2
                material_per_part = (part_width * part_length) / (sheet_length * sheet_width)
            else:
                total_parts = total_parts1
                material_per_part = (part_length * part_width) / (sheet_length * sheet_width)

            self.result_label.configure(text=f"Maximum Parts: {total_parts}")
            self.material_usage_label.configure(text=f"Material per Part: {material_per_part:.4f}")

            self.total_parts = total_parts
            self.material_per_part = material_per_part
            
            entry = {
                self.sheet_length: sheet_length,
                self.sheet_width: sheet_width,
                self.part_length: part_length,
                self.part_width: part_width,
                self.gap_size: gap_size,
                "Maximum Parts": total_parts,
                "Material per Part": material_per_part
            }
            self.save_to_json(entry)
            self.save_last_used_settings()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")

    def open_model_window(self):
        if self.model_window and self.model_window.winfo_exists():
            self.model_window.destroy()
            self.model_window = None
        else:
            self.model_window = ctk.CTkToplevel(self)
            self.model_window.title("Model")

            main_x = self.winfo_x()
            main_y = self.winfo_y()
            main_width = self.winfo_width()
            
            self.model_window.geometry(f"+{main_x + main_width + 10}+{main_y}")

            try:
                sheet_length = float(self.sheet_length_entry.get())
                sheet_width = float(self.sheet_width_entry.get())
                part_length = float(self.part_length_entry.get())
                part_width = float(self.part_width_entry.get())
                gap_size = float(self.gap_size_entry.get())
            except ValueError:
                messagebox.showerror("Input Error", "Please enter valid numerical values.")
                return

            canvas_width = 400
            canvas_height = int(canvas_width * (sheet_width / sheet_length))
            border_width = 5

            canvas = ctk.CTkCanvas(self.model_window, width=canvas_width + border_width * 2, height=canvas_height + border_width * 2, background='white')
            canvas.pack()

            canvas.create_rectangle(
                border_width, border_width,
                canvas_width + border_width, canvas_height + border_width,
                outline="black", width=border_width
            )

            scaled_part_length = (part_length / sheet_length) * canvas_width
            scaled_part_width = (part_width / sheet_width) * canvas_height
            scaled_gap_size = (gap_size / sheet_length) * canvas_width

            num_parts_x = int((canvas_width - scaled_gap_size) // (scaled_part_length + scaled_gap_size))
            num_parts_y = int((canvas_height - scaled_gap_size) // (scaled_part_width + scaled_gap_size))

            for i in range(num_parts_x):
                for j in range(num_parts_y):
                    x1 = border_width + i * (scaled_part_length + scaled_gap_size) + scaled_gap_size
                    y1 = border_width + j * (scaled_part_width + scaled_gap_size) + scaled_gap_size
                    x2 = x1 + scaled_part_length
                    y2 = y1 + scaled_part_width

                    canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="white", width=2)
                    
        self.calculate_and_save()
        
    def save_model_image(self, sheet_length, sheet_width, part_length, part_width, gap_size):
        img_width = 400
        img_height = int(img_width * (sheet_width / sheet_length))
        border_width = 5

        image = Image.new('RGB', (img_width + border_width * 2, img_height + border_width * 2), 'white')
        draw = ImageDraw.Draw(image)

        draw.rectangle(
            [border_width, border_width, img_width + border_width, img_height + border_width],
            outline="black", width=border_width
        )
        
        scaled_part_length = int((part_length / sheet_length) * img_width)
        scaled_part_width = int((part_width / sheet_width) * img_height)
        scaled_gap_size = int((gap_size / sheet_length) * img_width)

        num_parts_x = int((img_width - scaled_gap_size) // (scaled_part_length + scaled_gap_size))
        num_parts_y = int((img_height - scaled_gap_size) // (scaled_part_width + scaled_gap_size))

        for i in range(num_parts_x):
            for j in range(num_parts_y):
                x1 = i * (scaled_part_length + scaled_gap_size) + scaled_gap_size + border_width
                y1 = j * (scaled_part_width + scaled_gap_size) + scaled_gap_size + border_width
                x2 = x1 + scaled_part_length
                y2 = y1 + scaled_part_width
                draw.rectangle([x1, y1, x2, y2], outline="black", fill="white")

        image.save("model_image.png")

    def toggle_view_history(self):
        if self.view_history_var.get():
            self.history_textbox.pack(pady=10, padx=10, fill="x")
            self.clear_history_button.pack(pady=10)
            self.display_history()
        else:
            self.history_textbox.pack_forget()
            self.clear_history_button.pack_forget()

    def display_history(self):
        with open(self.history_file, "r") as file:
            data = json.load(file)

        self.history_textbox.delete(1.0, "end")
        for entry in data:
            self.history_textbox.insert("end", f"{entry}\n")

    def save_to_json(self, entry):
        try:
            if not os.path.exists(self.history_file):
                with open(self.history_file, "w") as file:
                    json.dump([entry], file, indent=4)
            else:
                with open(self.history_file, "r") as file:
                    data = json.load(file)

                data.append(entry)

                with open(self.history_file, "w") as file:
                    json.dump(data, file, indent=4)

        except Exception as e:
            messagebox.showerror("File Error", f"Failed to save to JSON file: {str(e)}")

    def clear_history(self):
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the history?"):
            with open(self.history_file, "w") as file:
                json.dump([], file, indent=4)
            self.display_history()

    def load_last_used_settings(self):
        try:
            with open("settings.json", "r") as file:
                loaded_settings = json.load(file)
            merged_settings = {**self.default_settings, **loaded_settings}
            return merged_settings
        except (FileNotFoundError, json.JSONDecodeError):
            return self.default_settings

    def save_last_used_settings(self):
        try:
            self.settings[self.on_top] = self.always_on_top_var.get()
            self.settings[self.theme] = self.theme_var.get()
            self.settings[self.sheet_length] = self.sheet_length_entry.get()
            self.settings[self.sheet_width] = self.sheet_width_entry.get()
            self.settings[self.part_length] = self.part_length_entry.get()
            self.settings[self.part_width] = self.part_width_entry.get()
            self.settings[self.gap_size] = self.gap_size_entry.get()

            with open("settings.json", "w") as file:
                json.dump(self.settings, file, indent=4)
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"Failed to save settings: {str(e)}")

    def generate_html_report(self):
        self.calculate_and_save()
        try:
            sheet_length = float(self.sheet_length_entry.get())
            sheet_width = float(self.sheet_width_entry.get())
            part_length = float(self.part_length_entry.get())
            part_width = float(self.part_width_entry.get())
            gap_size = float(self.gap_size_entry.get())
            total_parts = self.total_parts
            material_per_part = self.material_per_part

            self.save_model_image(sheet_length, sheet_width, part_length, part_width, gap_size)

            html_content = f"""
            <html>
            <head>
                <title>Material Usage Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ width: 80%; margin: auto; }}
                    .section {{ margin-bottom: 20px; }}
                    .image {{ max-width: 100%; height: auto; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Material Usage Report</h1>
                    <div class="section">
                        <h2>Material Details</h2>
                        <p><strong>Length:</strong> {sheet_length} units</p>
                        <p><strong>Width:</strong> {sheet_width} units</p>
                    </div>
                    <div class="section">
                        <h2>Part Details</h2>
                        <p><strong>Length:</strong> {part_length} units</p>
                        <p><strong>Width:</strong> {part_width} units</p>
                        <p><strong>Gap Size:</strong> {gap_size} units</p>
                        <div class="section">
                        <h2>Results</h2>
                        <p><strong>Maximum Parts:</strong> {total_parts} parts</p>
                        <p><strong>Material Per Part:</strong> {material_per_part:.4f}</p>
                    </div>
                    <div class="section">
                        <h2>Model Image</h2>
                        <img src="model_image.png" class="image" alt="Model Image">
                    </div>
                </div>
            </body>
            </html>
            """

            with open("report.html", "w") as file:
                file.write(html_content)
            webbrowser.open("report.html")

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numerical values.")

            
if __name__ == "__main__":
    app = MaterialUsageCalculator()
    app.mainloop()