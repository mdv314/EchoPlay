import os
import json
import customtkinter as ctk
import multiprocessing
from tkinter import messagebox, simpledialog
from handler import process_queue, input_cleaner
from writer import write_to_queue

# Initialize CustomTkinter
ctk.set_appearance_mode("dark")  # Options: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

def load_profiles():
    """Load profile names from the 'profiles' directory and append the 'Edit Profiles' option."""
    defaults_dir = os.path.join("profiles", "defaults")
    profiles_dir = "profiles"

    os.makedirs(profiles_dir, exist_ok=True)
    os.makedirs(defaults_dir, exist_ok=True)

    default_profiles = [os.path.splitext(f)[0] for f in os.listdir(defaults_dir) if os.path.isfile(os.path.join(defaults_dir, f))]
    user_profiles = [os.path.splitext(f)[0] for f in os.listdir(profiles_dir) if os.path.isfile(os.path.join(profiles_dir, f))]

    return default_profiles + user_profiles + ["Edit Profiles..."]

def create_ctk_table(parent, data):
    """Creates a scrollable table using CTkScrollableFrame for displaying and editing 'keywords' and 'keymap'."""
    scrollable_frame = ctk.CTkScrollableFrame(parent)
    scrollable_frame.pack(fill="both", expand=True, padx=10, pady=5)

    # Table Header
    header_frame = ctk.CTkFrame(scrollable_frame)
    header_frame.pack(fill="x", padx=5, pady=2)

    ctk.CTkLabel(header_frame, text="Keyword", width=200, font=("Arial", 14)).pack(side="left", padx=5)
    ctk.CTkLabel(header_frame, text="Keymap", width=350, font=("Arial", 14)).pack(side="left", padx=5)

    # Store row widgets for data access
    row_widgets = []

    def delete_row(row_frame, row_data):
        """Removes the selected row from the table and data list."""
        row_frame.destroy()
        data.remove(row_data)

    # Populate Table with Rows
    for entry in data:
        row_frame = ctk.CTkFrame(scrollable_frame)
        row_frame.pack(fill="x", padx=5, pady=2)

        keyword_entry = ctk.CTkEntry(row_frame, width=200)
        keyword_entry.insert(0, entry["keyword"])
        keyword_entry.pack(side="left", padx=5)

        keymap_entry = ctk.CTkEntry(row_frame, width=350)
        keymap_entry.insert(0, str(entry["keymap"]))
        keymap_entry.pack(side="left", padx=5)

        delete_button = ctk.CTkButton(row_frame, text="X", width=30, fg_color="red", hover_color="darkred",
                                      command=lambda r=row_frame, d=entry: delete_row(r, d))
        delete_button.pack(side="left", padx=5)

        row_widgets.append((keyword_entry, keymap_entry))

    return scrollable_frame, row_widgets  # Returns table frame & list of entries for saving


# def open_json_table_editor(profile_name, profile_path, data):
#     """Opens a window with a table to edit only 'keywords' and 'keymap'."""
#     editor_window = ctk.CTkToplevel(tk_root)
#     editor_window.title(f"Editing {profile_name}")
#     editor_window.geometry("900x600")

#     ctk.CTkLabel(editor_window, text=f"Editing: {profile_name}", font=("Arial", 14)).pack(pady=5)

#     keywords_data = data.get("keywords", [])

#     # Create the custom table
#     table_frame, entry_widgets = create_ctk_table(editor_window, keywords_data)

#     # Frame for adding new keywords
#     add_frame = ctk.CTkFrame(editor_window)
#     add_frame.pack(pady=5, fill="x")

#     ctk.CTkLabel(add_frame, text="Keyword:").pack(side="left")
#     keyword_entry = ctk.CTkEntry(add_frame)
#     keyword_entry.pack(side="left", padx=5)

#     ctk.CTkLabel(add_frame, text="Keymap:").pack(side="left")
#     keymap_entry = ctk.CTkEntry(add_frame, width=40)
#     keymap_entry.pack(side="left", padx=5)

#     def add_new_entry():
#         """Adds a new keyword-keymap pair to the table."""
#         new_keyword = input_cleaner(keyword_entry.get())
#         new_keymap = keymap_entry.get().strip()

#         if new_keyword and new_keymap:
#             try:
#                 new_keymap_list = eval(new_keymap)
#                 if isinstance(new_keymap_list, list):
#                     tree.insert("", "end", values=(new_keyword, str(new_keymap_list)))
#                     keywords_data.append({"keyword": new_keyword, "keymap": new_keymap_list})
#                     keyword_entry.delete(0, "end")
#                     keymap_entry.delete(0, "end")
#                 else:
#                     messagebox.showerror("Error", "Keymap must be a list.")
#             except:
#                 messagebox.showerror("Error", "Invalid keymap format. Use list format.")

#     ctk.CTkButton(add_frame, text="Add", command=add_new_entry).pack(side="left", padx=5)

#     # Table for editing existing keywords
#     tree = ctk.CTkFrame(editor_window)
#     tree.pack(pady=5, fill="both", expand=True)

#     def save_json():
#         """Save the edited JSON back to the file."""
#         new_data = {"mode": data.get("mode", ""), "keywords": keywords_data}
#         with open(profile_path, "w") as f:
#             json.dump(new_data, f, indent=4)
#         messagebox.showinfo("Success", f"Changes saved to {profile_name}")
#         editor_window.destroy()

#     ctk.CTkButton(editor_window, text="Save Changes", command=save_json).pack(pady=5)

def open_json_table_editor(profile_name, profile_path, data):
    """Opens a window with a scrollable table to edit 'keywords' and 'keymap'."""
    editor_window = ctk.CTkToplevel(tk_root)
    editor_window.title(f"Editing {profile_name}")
    editor_window.geometry("900x600")

    ctk.CTkLabel(editor_window, text=f"Editing: {profile_name}", font=("Arial", 14)).pack(pady=5)

    keywords_data = data.get("keywords", [])

    # **Create the custom CTk table**
    table_frame, entry_widgets = create_ctk_table(editor_window, keywords_data)

    def add_new_entry():
        """Adds a new keyword-keymap pair to the table dynamically."""
        new_keyword = keyword_entry.get().strip()
        new_keymap = keymap_entry.get().strip()

        if new_keyword and new_keymap:
            try:
                new_keymap_list = eval(new_keymap)  # Convert string input to list
                if isinstance(new_keymap_list, list):
                    keywords_data.append({"keyword": new_keyword, "keymap": new_keymap_list})
                    table_frame.destroy()  # Rebuild the table
                    global entry_widgets  # Ensure global update
                    table_frame, entry_widgets = create_ctk_table(editor_window, keywords_data)
                else:
                    messagebox.showerror("Error", "Keymap must be a list.")
            except:
                messagebox.showerror("Error", "Invalid keymap format. Use list format.")
        else:
            messagebox.showwarning("Warning", "Keyword and Keymap cannot be empty.")

    # **Frame for adding new keywords**
    add_frame = ctk.CTkFrame(editor_window)
    add_frame.pack(pady=5, fill="x")

    ctk.CTkLabel(add_frame, text="Keyword:").pack(side="left")
    keyword_entry = ctk.CTkEntry(add_frame, width=200)
    keyword_entry.pack(side="left", padx=5)

    ctk.CTkLabel(add_frame, text="Keymap:").pack(side="left")
    keymap_entry = ctk.CTkEntry(add_frame, width=350)
    keymap_entry.pack(side="left", padx=5)

    ctk.CTkButton(add_frame, text="Add", command=add_new_entry).pack(side="left", padx=5)

    def save_json():
        """Saves edited data to the JSON file."""
        new_data = {"mode": data.get("mode", ""), "keywords": []}

        # Extract updated values from table
        for keyword_entry, keymap_entry in entry_widgets:
            keyword = keyword_entry.get().strip()
            keymap = keymap_entry.get().strip()
            try:
                keymap_list = eval(keymap)  # Convert string to list format
                if isinstance(keymap_list, list):
                    new_data["keywords"].append({"keyword": keyword, "keymap": keymap_list})
                else:
                    messagebox.showerror("Error", "Keymap must be a list format.")
            except:
                messagebox.showerror("Error", "Invalid keymap format.")

        with open(profile_path, "w") as f:
            json.dump(new_data, f, indent=4)

        messagebox.showinfo("Success", f"Changes saved to {profile_name}")
        editor_window.destroy()

    # **Delete Profile Function**
    def delete_profile():
        """Deletes the current profile and closes the editor."""
        confirm = messagebox.askyesno("Delete Profile", f"Are you sure you want to delete '{profile_name}'?")
        if confirm:
            os.remove(profile_path)
            refresh_profiles()
            editor_window.destroy()  # Close the editor window

    # **Bottom Button Frame**
    button_frame = ctk.CTkFrame(editor_window)
    button_frame.pack(fill="x", side="bottom", pady=10, padx=10)

    ctk.CTkButton(button_frame, text="Save Changes", command=save_json).pack(side="left", padx=5)

    # **Red Delete Button in Bottom-Right Corner**
    ctk.CTkButton(button_frame, text="Delete Profile", command=delete_profile, fg_color="red", hover_color="darkred").pack(side="right", padx=5)


def edit_profiles():
    """Opens a profile management window with selectable profiles and an Add/Delete button panel."""
    edit_window = ctk.CTkToplevel(tk_root)
    edit_window.title("Edit Profiles")
    edit_window.geometry("500x500")

    ctk.CTkLabel(edit_window, text="Manage Profiles", font=("Arial", 16)).pack(pady=10)

    profiles_dir = "profiles"
    profiles = [f for f in os.listdir(profiles_dir) if f.endswith(".json")]

    if not profiles:
        ctk.CTkLabel(edit_window, text="No profiles found.", font=("Arial", 14)).pack()
        return

    # **Scrollable frame for selectable profiles**
    scroll_frame = ctk.CTkScrollableFrame(edit_window)
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

    def open_json_editor(profile_name):
        """Opens an editor for the selected JSON file."""
        profile_path = os.path.join(profiles_dir, profile_name)
        print(profile_path)
        try:
            with open(profile_path, "r") as f:
                data = json.load(f)  # Load JSON data
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Invalid JSON in {profile_name}")
            return

        open_json_table_editor(profile_name, profile_path, data)

    selected_profile_var = ctk.StringVar(value="")  # Stores selected profile

    for profile in profiles:
        def set_selected_profile(p=profile):
            selected_profile_var.set(p)

        ctk.CTkButton(scroll_frame, text=profile, command=lambda p=profile: open_json_editor(p)).pack(pady=5, fill="x")

    def delete_profile():
        """Deletes the selected profile from the list."""
        selected_profile = selected_profile_var.get()
        if not selected_profile:
            messagebox.showwarning("Warning", "No profile selected.")
            return

        confirm = messagebox.askyesno("Delete Profile", f"Are you sure you want to delete '{selected_profile}'?")
        if confirm:
            os.remove(os.path.join(profiles_dir, selected_profile))
            refresh_profiles()
            edit_window.destroy()  # Close and reopen to refresh
            edit_profiles()  # Reopen with updated list

    # **Add Profile Button**
    def add_profile():
        """Allows users to copy a default profile to create a new profile using buttons instead of text input."""
        defaults_dir = os.path.join("profiles", "defaults")
        profiles_dir = "profiles"

        os.makedirs(defaults_dir, exist_ok=True)

        # Get available default profiles
        default_profiles = [f for f in os.listdir(defaults_dir) if f.endswith(".json")]

        if not default_profiles:
            messagebox.showerror("Error", "No default profiles available. Please add defaults to the 'defaults' folder.")
            return

        # Create a selection window
        select_window = ctk.CTkToplevel(tk_root)
        select_window.title("Select Default Profile")
        select_window.geometry("350x250")

        ctk.CTkLabel(select_window, text="Select a default profile:", font=("Arial", 14)).pack(pady=10)

        button_frame = ctk.CTkScrollableFrame(select_window)
        button_frame.pack(fill="both", expand=True, padx=10, pady=5)

        def create_new_profile(selected_default):
            """Handles copying a selected default profile and creating a new profile."""
            select_window.destroy()  # Close the selection window

            # Ask for a new profile name
            new_profile_name = simpledialog.askstring("New Profile", "Enter a name for the new profile:")
            if new_profile_name:
                new_profile_path = os.path.join(profiles_dir, f"{new_profile_name}.json")
                default_profile_path = os.path.join(defaults_dir, selected_default)

                # Copy default profile to new profile
                with open(default_profile_path, "r") as f:
                    default_data = json.load(f)

                with open(new_profile_path, "w") as f:
                    json.dump(default_data, f, indent=4)

                # Refresh profiles
                refresh_profiles()

                # Open the new profile in the JSON editor
                open_json_table_editor(f"{new_profile_name}.json", new_profile_path, default_data)

                # Reopen the Edit Profiles window to update the list
                edit_window.destroy()
                edit_profiles()

        # Create a button for each default profile
        for profile in default_profiles:
            ctk.CTkButton(button_frame, text=profile, command=lambda p=profile: create_new_profile(p)).pack(pady=5, fill="x")

    # **Button Frame (Side-by-Side Buttons)**
    button_frame = ctk.CTkFrame(edit_window)
    button_frame.pack(pady=10, fill="x", padx=10)

    ctk.CTkButton(button_frame, text="Add Profile", command=add_profile).pack(side="left", expand=True, padx=5)
    # ctk.CTkButton(button_frame, text="Delete Profile", command=delete_profile).pack(side="right", expand=True, padx=5)




def start_handler(profile_name):
    """Starts the handler and writer processes with a shared queue."""
    global queue, handler_process, writer_process
    queue = multiprocessing.Queue()
    handler_process = multiprocessing.Process(target=process_queue, args=(queue, profile_name))
    handler_process.start()
    writer_process = multiprocessing.Process(target=write_to_queue, args=(queue,))
    writer_process.start()

def play_action():
    selected_profile = profile_var.get()
    if selected_profile == "Edit Profiles...":
        edit_profiles()
    elif selected_profile:
        messagebox.showinfo("Play", f"Playing with profile: {selected_profile}")
        start_handler(selected_profile)
    else:
        messagebox.showwarning("Warning", "Please select a profile.")

def stop():
    handler_process.kill()
    writer_process.kill()
    while not queue.empty():
        queue.get_nowait()

def refresh_profiles():
    """Refresh the profile dropdown options."""
    profile_menu.configure(values=load_profiles())
    profile_var.set("")  # Reset selection

if __name__ == "__main__":
    tk_root = ctk.CTk()
    tk_root.title("EchoPlay")
    tk_root.geometry("800x400")

    profile_var = ctk.StringVar()

    ctk.CTkLabel(tk_root, text="Select Profile:", font=("Arial", 16)).pack(pady=5)
    profile_menu = ctk.CTkComboBox(tk_root, variable=profile_var, values=load_profiles())
    profile_menu.pack(pady=5)

    play_button = ctk.CTkButton(tk_root, text="Play", command=play_action)
    play_button.pack(pady=5)

    stop_button = ctk.CTkButton(tk_root, text="Stop", command=stop)
    stop_button.pack(pady=5)

    refresh_button = ctk.CTkButton(tk_root, text="Refresh Profiles", command=refresh_profiles)
    refresh_button.pack(pady=5)

    tk_root.mainloop()
