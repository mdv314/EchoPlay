import os
import json
import customtkinter as ctk
import multiprocessing
from tkinter import messagebox, simpledialog
from handler import process_queue, input_cleaner
import ast
from writer import run
import json
import sys

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

def open_json_table_editor(profile_name, profile_path, data):
    """Opens a window with a scrollable table to edit 'keywords' and 'keymap'."""
    editor_window = ctk.CTkToplevel(tk_root)
    editor_window.title(f"Editing {profile_name}")
    editor_window.geometry("900x600")

    # bring it to focus:
    editor_window.lift()
    editor_window.focus_set()
    editor_window.grab_set()

    ctk.CTkLabel(editor_window, text=f"Editing: {profile_name}", font=("Arial", 14)).pack(pady=5)

    keywords_data = data.get("keywords", [])

    # **Create the custom CTk table**
    global table_frame, entry_widgets
    table_frame, entry_widgets = create_ctk_table(editor_window, keywords_data)

    def add_new_entry():
        """Adds a new keyword-keymap pair to the table dynamically."""
        global table_frame
        new_keyword = input_cleaner(keyword_entry.get())
        new_keymap = keymap_entry.get().strip()

        if new_keyword and new_keymap:
            try:
                new_keymap_list = ast.literal_eval(new_keymap)
                print(type(new_keymap_list))  # Safer way to evaluate the string input
                if isinstance(new_keymap_list, list):
                    print("If Statement Clear")
                    keywords_data.append({"keyword": new_keyword, "keymap": new_keymap_list})
                    print("Append Clear")
                    table_frame.destroy()  # Rebuild the table
                    print("Destroy Clear")
                    global entry_widgets  # Ensure global update
                    # new_table_frame, entry_widgets = create_ctk_table(editor_window, keywords_data)
                    print("Table Frame Clear")
                else:
                    messagebox.showerror("Error", "Keymap must be a list.")
            except:
                messagebox.showerror("Error", "Invalid keymap format. Use list format.")
        else:
            messagebox.showerror("Warning", "Keyword and Keymap cannot be empty.")
        new_table_frame, entry_widgets = create_ctk_table(editor_window, keywords_data)
        
    # table_frame = new_table_frame


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
        """Saves edited data to the JSON file while handling deletions gracefully."""
        new_data = {"mode": data.get("mode", ""), "keywords": []}

        # Ensure there are remaining entries to save
        if not entry_widgets:
            messagebox.showerror("Warning", "No valid entries to save.")
        else:
            # Extract updated values from table, skipping deleted rows
            for keyword_entry, keymap_entry in entry_widgets:
                if keyword_entry.winfo_exists() and keymap_entry.winfo_exists():  # Check if widget still exists
                    keyword = keyword_entry.get().strip()
                    keymap = keymap_entry.get().strip()

                    if keyword and keymap:  # Ensure both fields are not empty
                        try:
                            keymap_list = eval(keymap)  # Convert string to list format
                            if isinstance(keymap_list, list):
                                new_data["keywords"].append({"keyword": keyword, "keymap": keymap_list})
                            else:
                                messagebox.showerror("Error", "Keymap must be a list format.")
                        except Exception:
                            messagebox.showerror("Error", "Invalid keymap format.")

        # Write updated data to file only if valid keywords exist
        if new_data["keywords"]:
            with open(profile_path, "w") as f:
                json.dump(new_data, f, indent=4)
            messagebox.showinfo("Success", f"Changes saved to {profile_name}")
        else:
            messagebox.showearning("Warning", "No valid data to save.")

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

    # bring it to focus:
    edit_window.lift()
    edit_window.focus_set()
    edit_window.grab_set()

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

    # not used 
    def delete_profile():
        """Deletes the selected profile from the list."""
        selected_profile = selected_profile_var.get()
        if not selected_profile:
            messagebox.showerror("Warning", "No profile selected.")
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

        # bring it to focus:
        select_window.lift()
        select_window.focus_set()
        select_window.grab_set()

        ctk.CTkLabel(select_window, text="Select a default profile:", font=("Arial", 14)).pack(pady=10)

        button_frame = ctk.CTkScrollableFrame(select_window)
        button_frame.pack(fill="both", expand=True, padx=10, pady=5)

        def create_new_profile(selected_default):
            """Handles copying a selected default profile and creating a new profile."""
            select_window.destroy()  # Close the selection window

            # Ask for a new profile name
            new_profile_name = simpledialog.askstring("New Profile", "Enter a name for the new profile:")
            if new_profile_name:
                try:
                    new_profile_path = os.path.join(profiles_dir, f"{new_profile_name}.json")
                    default_profile_path = os.path.join(defaults_dir, selected_default)
                except:
                    messagebox.showerror("Error", "Invalid characters in profile name.")

                # Copy default profile to new profile
                with open(default_profile_path, "r") as f:
                    default_data = json.load(f)

                try:
                    with open(new_profile_path, "w") as f:
                        json.dump(default_data, f, indent=4)
                except:
                    messagebox.showerror("Error", "Invalid characters in profile name.")

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
    synonyms = True if "-s" in sys.argv else False
    queue = multiprocessing.Queue()
    handler_process = multiprocessing.Process(target=process_queue, args=(queue, profile_name, synonyms))
    handler_process.start()
    writer_process = multiprocessing.Process(target=run, args=(queue,))
    writer_process.start()


def play_action():
    stop_button.pack(pady=5, before=play_button)
    play_button.pack_forget()
    selected_profile = profile_var.get()
    if selected_profile == "Edit Profiles...":
        edit_profiles()
    elif selected_profile:
        messagebox.showinfo("Play", f"Playing with profile: {selected_profile}")
        start_handler(selected_profile)
    else:
        messagebox.showerror("Warning", "Please select a profile.")

    

def about_action():
    about_window = tk.Toplevel(tk_root)
    about_window.title("About")
    about_window.geometry("300x150")
    tk.Label(about_window, text="This is a simple GUI app.", font=("Arial", 12)).pack(pady=20)

def stop():
    play_button.pack(pady=5, before=stop_button)   # Show Play button
    stop_button.pack_forget()  # Hide Stop button
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
    profile_menu.bind("<Key>", lambda e: "break")
    profile_menu.pack(pady=5)

    play_button = ctk.CTkButton(tk_root, text="Play", command=play_action)
    play_button.pack(pady=5)

    stop_button = ctk.CTkButton(tk_root, text="Stop", command=stop)
    stop_button.pack(pady=5)

    refresh_button = ctk.CTkButton(tk_root, text="Refresh Profiles", command=refresh_profiles)
    refresh_button.pack(pady=5)

    tk_root.mainloop()