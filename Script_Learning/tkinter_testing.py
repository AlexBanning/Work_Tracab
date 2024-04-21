import tkinter as tk


"""
Returning string value in a simple box-gui with a button to copy the string
"""
def copy_text():
    text = text_entry.get("1.0", "end-1c")  # Get text from Text widget
    root.clipboard_clear()  # Clear the clipboard
    root.clipboard_append(text)  # Append text to clipboard

root = tk.Tk()
root.title("String Value GUI")

# Create a Text widget to display string values
text_entry = tk.Text(root, height=10, width=50)
text_entry.pack(pady=10)

# Insert some example text
example_text = "Hello, world!\nThis is a sample text."
text_entry.insert("1.0", example_text)

# Create a button to copy text
copy_button = tk.Button(root, text="Copy Text", command=copy_text)
copy_button.pack(pady=5)

root.mainloop()