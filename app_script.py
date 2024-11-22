import subprocess
import sys
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, Menu, Toplevel, Label, StringVar
from PIL import Image,ImageTk
import os
import ffmpeg

settings = {
    'bitrate': '192',
    'sample_rate': '44.1',
    'channels': '2'
}

def get_ffmpeg_path():
    if getattr(sys, 'frozen', False):
        ffmpeg_path = os.path.join(sys._MEIPASS, "ffmpeg.exe")
    else:
        ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg.exe") 
    return ffmpeg_path

def get_ffmpeg_probe():
    if getattr(sys, 'frozen', False):
        ffprobe_path = os.path.join(sys._MEIPASS, "ffprobe.exe")
    else:
        ffprobe_path = os.path.join(os.getcwd(), "ffprobe.exe") 
    return ffprobe_path

def select_file():
    file_paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3;*.wav;*.aac;*.flac;*.ogg;*.m4a")])
    if file_paths:
        input_entry.config(state='normal')
        input_entry.delete(0, ttk.END)
        input_entry.insert(0, ';'.join(file_paths))
        input_entry.config(state='readonly')

def convert_to():
    file_paths = input_entry.get().split(';')
    if not file_paths[0]:
        messagebox.showwarning("Input Error", "Please select audio files.")
        return

    ffmpeg_path = get_ffmpeg_path()
    selected_format = format_var.get()

    total_files = len(file_paths)
    progress_bar['maximum'] = total_files
    
    make_progress_bar_visible()
    
    for index, input_file in enumerate(file_paths):
        if not input_file:
            continue
        
        output_file = filedialog.asksaveasfilename(defaultextension=f".{selected_format}", filetypes=[(f"{selected_format.upper()} File", f"*.{selected_format}")])

        if not output_file:
            messagebox.showinfo("Conversion Aborted", "Conversion aborted.")
            input_entry.config(state='normal')
            input_entry.delete(0, ttk.END)
            input_entry.config(state='readonly')
            reset_progress()
            make_progress_bar_transparent()
            return

        sample_rate_int = int(float(settings['sample_rate']) * 1000)
        
        if output_file:
            try:
                ffmpeg_command = (
                    ffmpeg.input(input_file)
                    .output(output_file, acodec=selected_format, ab=f"{settings['bitrate']}k", ar=sample_rate_int, ac=settings['channels'])
                    .compile()
                )#prva

                full_command = [ffmpeg_path] + ffmpeg_command[1:]

                subprocess.run(full_command, creationflags=subprocess.CREATE_NO_WINDOW, check=True)

                progress_bar['value'] = index + 1
                progress_label.config(text=f"Converting {index + 1} of {total_files} files...")
                root.update_idletasks()

                original_size = get_file_size(input_file)
                converted_size = get_file_size(output_file)
                percentage = 100 - (converted_size / original_size * 100) if original_size > 0 else 0

                original_size_mb = original_size / (1024 * 1024)
                converted_size_mb = converted_size / (1024 * 1024)

                input_file_name = os.path.basename(input_file)
                output_file_name = os.path.basename(output_file)
                tree.insert("", ttk.END, iid=output_file, values=(
                    input_file_name, output_file_name, 
                    f"{original_size_mb:.2f} MB", f"{converted_size_mb:.2f} MB", 
                    f"{percentage:.2f}"))

            except Exception as e:
                messagebox.showerror("Conversion Error", f"An error occurred with {input_file}: {e}")
            
    if output_file:
        progress_label.config(text="Conversion Complete!")

    input_entry.config(state='normal')
    input_entry.delete(0, ttk.END)
    input_entry.config(state='readonly')

    root.after(500, lambda: (reset_progress(), make_progress_bar_transparent()))


def get_file_size(file_path):
    try:
        return os.path.getsize(file_path)
    except FileNotFoundError:
        return 0

def get_additional_info(file_path):
    try:
        ffprobe = get_ffmpeg_probe()
        probe = ffmpeg.probe(file_path,cmd=ffprobe)#druga
        stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
        
        if stream:
            codec = stream.get('codec_name', 'Unknown')
            sample_rate = stream.get('sample_rate', 'Unknown')
            channels = stream.get('channels', 'Unknown')
            bitrate = stream.get('bit_rate', 'Unknown')
            
            duration = stream.get('duration', 'Unknown')
            duration = float(duration) if duration != 'Unknown' else 'Unknown'
            if duration != 'Unknown':
                duration = f"{int(duration // 60)}:{int(duration % 60):02d}"

            if bitrate != 'Unknown':
                bitrate = f"{int(bitrate) / 1000:.2f} kbps"
            else:
                bitrate = 'Unknown'

            return {
                'Codec': codec,
                'Sample Rate': f"{sample_rate} Hz",
                'Channels': channels,
                'Bitrate': bitrate,
                'Duration': duration
            }
        else:
            return {'Error': 'No audio stream found'}
    except Exception as e:
        return {'Error': str(e)}

def make_progress_bar_transparent():
    progress_bar.configure(style="Transparent.Horizontal.TProgressbar")

def make_progress_bar_visible():
    progress_bar.configure(style="Visible.Horizontal.TProgressbar")

def reset_progress():
    progress_bar['value'] = 0
    progress_label.config(text="")

def clear_table():
    if not tree.get_children():
        messagebox.showwarning("Clear Error", "No files to clear.")
    else:
        for item in tree.get_children():
            tree.delete(item)

def clear_selected_rows():
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showwarning("Clear Error", "No rows selected.")
    else:
        for item in selected_items:
            tree.delete(item)

def play_file(event):
    selected_item = tree.selection()
    if selected_item:
        output_file = selected_item[0]
        if os.path.exists(output_file):
            os.startfile(output_file) 
        else:
            messagebox.showerror("Error", "Cannot play file on this system.")#treca

def show_additional_info():
    selected_item = tree.selection()
    if selected_item:
        output_file = selected_item[0]
        print(output_file)
        
        if os.path.exists(output_file):
            info = get_additional_info(output_file)
            
            info_window = Toplevel(root)
            info_window.title(f"Details: {tree.item(selected_item[0])['values'][1]}")
            info_window.geometry("350x350")
            info_window.resizable(False,False)
            info_window.attributes('-topmost', True)

            info_text = (
                f"Duration: {info.get('Duration', 'N/A')}\n"
                f"Codec: {info.get('Codec', 'N/A')}\n"
                f"Sample Rate: {info.get('Sample Rate', 'N/A')}\n"
                f"Channels: {info.get('Channels', 'N/A')}\n"
                f"Bitrate: {info.get('Bitrate', 'N/A')}\n"
            )

            info_label = Label(info_window, text=info_text, font=('Helvetica', 12), anchor='center', justify='left', wraplength=350)
            info_label.pack(expand=True,pady=20, padx=20)

def on_right_click(event):
    context_menu.post(event.x_root, event.y_root)

def update_progress_bar_width(event):
    window_width = root.winfo_width()
    new_width = int(window_width * 0.6)
    progress_bar.config(length=new_width)

def open_settings_window():
    settings_window = Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("350x350")
    settings_window.resizable(False, False)

    center_frame = ttk.Frame(settings_window)
    center_frame.pack(expand=True, fill='both', pady=(30, 0))

    def apply_settings():
        settings['bitrate'] = bitrate_var.get()
        settings['sample_rate'] = sample_rate_var.get()
        settings['channels'] = channels_var.get()
        settings_window.destroy()

    def update_settings_options(*args):
        selected_format = format_var.get()
        
        if selected_format == 'mp3':
            bitrate_menu.config(values=['96', '128', '192', '256', '320'])
            sample_rate_menu.config(values=['44.1', '48'])
            channels_menu.config(values=['1', '2'])
        elif selected_format == 'wav':
            bitrate_menu.config(values=['None'])
            sample_rate_menu.config(values=['44.1', '48', '96'])
            channels_menu.config(values=['1', '2', '4', '6'])
        elif selected_format == 'flac':
            bitrate_menu.config(values=['None'])
            sample_rate_menu.config(values=['44.1', '48', '96'])
            channels_menu.config(values=['1', '2'])
        elif selected_format == 'aac':
            bitrate_menu.config(values=['128', '192', '256', '320', '512'])
            sample_rate_menu.config(values=['44.1', '48'])
            channels_menu.config(values=['1', '2'])
        elif selected_format == 'ac3':
            bitrate_menu.config(values=['192', '256', '384', '448', '640'])
            sample_rate_menu.config(values=['44.1', '48'])
            channels_menu.config(values=['2', '5', '6'])

        bitrate_var.set(bitrate_menu.cget('values')[0])
        sample_rate_var.set(sample_rate_menu.cget('values')[0])
        channels_var.set(channels_menu.cget('values')[0])

    ttk.Label(center_frame, text="Bitrate (kbps):").pack(pady=5)
    bitrate_var = StringVar(value=settings['bitrate'])
    bitrate_menu = ttk.Combobox(center_frame, textvariable=bitrate_var, state='readonly')
    bitrate_menu.pack(pady=5)

    ttk.Label(center_frame, text="Sample Rate (kHz):").pack(pady=5)
    sample_rate_var = StringVar(value=settings['sample_rate'])
    sample_rate_menu = ttk.Combobox(center_frame, textvariable=sample_rate_var, state='readonly')
    sample_rate_menu.pack(pady=5)

    ttk.Label(center_frame, text="Channels:").pack(pady=5)
    channels_var = StringVar(value=settings['channels'])
    channels_menu = ttk.Combobox(center_frame, textvariable=channels_var, state='readonly')
    channels_menu.pack(pady=5)

    apply_button = ttk.Button(center_frame, text="Apply", command=apply_settings)
    apply_button.pack(pady=10)

    update_settings_options()

def trim_audio():
    file_paths = input_entry.get().split(';')

    if len(file_paths) > 1:
        messagebox.showwarning("Input Error", "Please select only one audio file.")
        return
    
    if not file_paths[0]:
        messagebox.showwarning("Input Error", "Please select an audio file.")
        return
    
    file_name = os.path.basename(file_paths[0])
    file_extension = os.path.splitext(file_name)[1]
    
    trim_window = ttk.Toplevel(root)
    trim_window.title(f"{file_name}")
    trim_window.geometry("300x250")
    trim_window.resizable(False,False)

    start_label = ttk.Label(trim_window, text="Start Time (MM:SS):")
    start_label.pack(pady=10)

    start_time_entry = ttk.Entry(trim_window, width=10)
    start_time_entry.pack(pady=5)

    end_label = ttk.Label(trim_window, text="End Time (MM:SS):")
    end_label.pack(pady=10)

    end_time_entry = ttk.Entry(trim_window, width=10)
    end_time_entry.pack(pady=5)

    def start_trimming():
        start_time = start_time_entry.get()
        end_time = end_time_entry.get()

        def validate_time(time_str):
            if len(time_str) == 5 and time_str[2] == ":" and time_str[:2].isdigit() and time_str[3:].isdigit():
                minutes = int(time_str[:2])
                seconds = int(time_str[3:])
                return 0 <= minutes < 60 and 0 <= seconds < 60
            return False

        if not validate_time(start_time) or not validate_time(end_time):
            messagebox.showwarning("Input Error", "Please enter time in MM:SS format.")
            return
        
        def time_to_seconds(time_str):
            minutes = int(time_str[:2])
            seconds = int(time_str[3:])
            return minutes * 60 + seconds

        start_seconds = time_to_seconds(start_time)
        end_seconds = time_to_seconds(end_time)

        if end_seconds <= start_seconds:
            messagebox.showwarning("Input Error", "End time must be greater than start time.")
            return
        
        input_file = file_paths[0]

        output_file = filedialog.asksaveasfilename(
            defaultextension=file_extension,  
            filetypes=[(f"{file_extension.upper()} Files", f"*{file_extension}")],
            title="Save Trimmed Audio As"
        )
        
        start_time_hms = f"00:{start_time}"
        end_time_hms = f"00:{end_time}"

        command = (
            ffmpeg.input(input_file, ss=start_time_hms, to=end_time_hms)  # Specify input and trimming times
            .output(output_file, c="copy")  # Output file with codec copy to preserve format
            .overwrite_output()  # Overwrite the output file if it already exists
        )

        try:
            ffmpeg.run(command)
            messagebox.showinfo("Success", f"Audio file {file_name} has been trimmed successfully.")
            os.startfile(output_file)
            trim_window.destroy() 
        
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"An error occurred while trimming the audio file: {e}")
    
    button_frame = ttk.Frame(trim_window)
    button_frame.pack(pady=20)

    start_button = ttk.Button(button_frame, text="Trim", command=start_trimming,width=10)
    start_button.pack(side="left", padx=10)

def merge_audio():
    file_paths = input_entry.get().split(';')
        
    if not file_paths[0]:
        messagebox.showwarning("Input Error", "Please select an audio file.")
        return
    
    if len(file_paths) == 1:
        messagebox.showwarning("Input Error", "Please select more than one audio file.")
        return
    
    file_extensions = [os.path.splitext(f)[1].lower() for f in file_paths]
    if len(set(file_extensions)) > 1:
        messagebox.showerror("Format Error", "All selected files must be in the same format.")
        return
    
    output_file = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 Files", "*.mp3"), ("WAV Files", "*.wav"), ("All Files", "*.*")], title="Save Merged Audio As")

    file_list_path = 'filelist.txt'
    with open(file_list_path, 'w') as f:
        for file in file_paths:
            f.write(f"file '{os.path.abspath(file)}'\n")
    
    command = (
        ffmpeg.input(file_list_path, f="concat", safe=0)  # Specify input with concat and safe options
        .output(output_file, c="copy")  # Use copy codec for output
        .overwrite_output()  # Overwrite the output file if it exists
    )

    try:
        ffmpeg.run(command)
        os.remove(file_list_path)
        messagebox.showinfo("Success", f"Audio files merged successfully: {output_file}")
        os.startfile(output_file)

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred while merging the audio files: {e}")
    
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
    
def edit_file():
    file_paths = input_entry.get().split(';')
    
    if len(file_paths) > 1:
        messagebox.showwarning("Input Error", "Please select only one audio file.")
        return
    
    if not file_paths[0]:
        messagebox.showwarning("Input Error", "Please select an audio file.")
        return
    
    file_name = os.path.basename(file_paths[0])
    
    edit_window = ttk.Toplevel(root)
    edit_window.title(f"Edit {file_name}")
    edit_window.geometry("300x320")
    edit_window.resizable(False, False)
    
    ttk.Label(edit_window, text="Title:").pack(pady=5)
    title_entry = ttk.Entry(edit_window, width=30)
    title_entry.pack(pady=5)

    ttk.Label(edit_window, text="Album:").pack(pady=5)
    album_entry = ttk.Entry(edit_window, width=30)
    album_entry.pack(pady=5)

    ttk.Label(edit_window, text="Artist:").pack(pady=5)
    artist_entry = ttk.Entry(edit_window, width=30)
    artist_entry.pack(pady=5)
    
    def apply_changes():
        album = album_entry.get()
        artist = artist_entry.get()
        title = title_entry.get()

        if not album or not artist or not title:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        
        try:
            file_name, file_extension = os.path.splitext(file_paths[0])

            temp_file = f"{file_name}_temp{file_extension}"

            command = [
                'ffmpeg', '-i', file_paths[0],  
                '-metadata', f'album={album}',
                '-metadata', f'artist={artist}',
                '-metadata', f'title={title}',
                '-y',  
                temp_file 
            ]#sesta
            subprocess.run(command, check=True)

            os.replace(temp_file, file_paths[0])
            
            messagebox.showinfo("Success", f"Metadata applied successfully to {file_paths[0]}")
            edit_window.destroy() 
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"An error occurred while applying changes: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    button_frame = ttk.Frame(edit_window)
    button_frame.pack(pady=20)

    apply_button = ttk.Button(button_frame, text="Apply", command=apply_changes,width=10)
    apply_button.pack(side="left",padx=10)

def audio_settings():
    file_paths = input_entry.get().split(';')

    if len(file_paths) > 1:
        messagebox.showwarning("Input Error", "Please select only one audio file.")
        return

    if not file_paths[0]:
        messagebox.showwarning("Input Error", "Please select an audio file.")
        return

    file_name = os.path.basename(file_paths[0])

    input_file = file_paths[0]

    current_speed = 1.0  
    current_volume = 0.0

    edit_window = ttk.Toplevel(root)
    edit_window.title(f"Audio Settings: {file_name}")
    edit_window.geometry("300x300")
    edit_window.resizable(False, False)

    speed_label = ttk.Label(edit_window, text="Playback Speed")
    speed_label.pack(pady=10)

    speed_slider = ttk.Scale(edit_window, from_=0.5, to=1.5, orient="horizontal", length=200)
    speed_slider.set(current_speed)
    speed_slider.pack(pady=10)

    speed_value_label = ttk.Label(edit_window, text=f"Current Speed: {current_speed}x")
    speed_value_label.pack(pady=5)

    def update_speed_label(val):
        rounded_val = round(val, 1)
        speed_value_label.config(text=f"Current Speed: {rounded_val}x")

    speed_slider.bind("<Motion>", lambda event: update_speed_label(speed_slider.get()))

    volume_label = ttk.Label(edit_window, text="Volume level (dB)")
    volume_label.pack(pady=10)

    volume_slider = ttk.Scale(edit_window, from_=-10.0, to=10.0, orient="horizontal", length=200)
    volume_slider.set(current_volume) 
    volume_slider.pack(pady=10)

    volume_value_label = ttk.Label(edit_window, text=f"Volume: {current_volume} dB")
    volume_value_label.pack(pady=5)


    def update_volume_label(val):
        rounded_val = round(val, 0)  
        volume_value_label.config(text=f"Volume: {rounded_val} dB")

    volume_slider.bind("<Motion>", lambda event: update_volume_label(volume_slider.get()))

    def apply_changes():
        speed_value = speed_slider.get()
        volume_value = volume_slider.get()
        rounded_speed = round(speed_value, 2)  
        rounded_volume = round(volume_value, 2) 

        out_file = f"edited_{file_name}"
        out_file_path = os.path.join(os.path.dirname(input_file), f"edited_{file_name}")

        command = (
                ffmpeg.input(input_file)  # Specify the input file
                .filter('atempo', rounded_speed)  # Apply the atempo filter for playback speed
                .filter('volume', f'{rounded_volume}dB')  # Apply the volume filter
                .output(out_file)  # Specify the output file
                .overwrite_output()  # Allow overwriting the output file
            )
        
        try:
            ffmpeg.run(command)

            messagebox.showinfo("Success", f"File saved successfully to {out_file_path}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to adjust audio settings: {e}")
        except FileNotFoundError as fnf_error:
            messagebox.showerror("Error", f"File not found: {fnf_error}")

        edit_window.destroy() 

    ok_button = ttk.Button(edit_window, text="OK", command=apply_changes)
    ok_button.pack(pady=20)

def show_spectogram():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No item selected.")
        return

    input_file = selected_item[0]
    file_name = os.path.basename(selected_item[0])

    output_image = os.path.join(os.getcwd(), "spectrogram_output.png")

    if input_file:
        command = (
            ffmpeg.input(input_file)  # Specify the input file
            .output(output_image, v='warning', lavfi='showspectrumpic=s=640x360:legend=1')  # Apply the showspectrumpic filter
            .overwrite_output()  # Allow overwriting the output image
        )

        try:
            ffmpeg.run(command)

            window = Toplevel()
            window.title(f"Spectrogram {file_name}")

            image = Image.open(output_image)
            photo = ImageTk.PhotoImage(image)
            label = Label(window, image=photo)
            label.image = photo 
            label.pack()
            
            def on_close():
                window.destroy()
                os.remove(output_image) 

            window.protocol("WM_DELETE_WINDOW", on_close)
            window.mainloop()

        except subprocess.CalledProcessError as e:
            os.remove(output_image) 
            messagebox.showerror("Error", f"Failed to create spectrogram: {e}")

def extract_audio():
    video_path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("Video Files", "*.mp4;*.mkv;*.avi;*.mov;*.flv;*.wmv"), ("All Files", "*.*")]
    )
    if not video_path:
        return  

    audio_path = filedialog.asksaveasfilename(
        title="Save Audio File As",
        defaultextension=".mp3",
        filetypes=[("Audio Files", "*.mp3;*.wav;*.aac"), ("All Files", "*.*")]
    )
    if not audio_path:
        return 

    ffmpeg_command = [
        "ffmpeg",
        "-i", video_path,  
        "-vn",  
        audio_path 
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        os.startfile(audio_path)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to extract audio.\n{e}")

root = ttk.Window(themename="superhero")
root.title("Audio App")
root.geometry('1000x720')
root.minsize(650,720)

input_label = ttk.Label(root, text="Select file(s):", font=('Helvetica', 14))
input_label.pack(pady=10)

input_frame = ttk.Frame(root)
input_frame.pack(pady=5, padx=20, fill='x')

input_entry = ttk.Entry(input_frame, width=0, font=('Helvetica', 12), state='readonly')
input_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))

select_button = ttk.Button(input_frame, text="Browse", command=select_file, bootstyle=LIGHT, width=15)
select_button.pack(side='right')

button_frame = ttk.Frame(root)
button_frame.pack(pady=20)

convert_button = ttk.Button(button_frame, text="Convert", command=convert_to, bootstyle=SUCCESS, width=20)  # Adjust width here
convert_button.pack(side='left', padx=10)

format_var = StringVar(value="ac3")
format_menu = ttk.Combobox(button_frame, textvariable=format_var, values=['ac3', 'mp3', 'wav', 'aac', 'flac', 'ogg'], state='readonly', width=15)
format_menu.pack(side='left', padx=10)

settings_button = ttk.Button(button_frame, text="Settings", command=open_settings_window, bootstyle=PRIMARY, width=20)  # Same width as convert_button
settings_button.pack(side='left', padx=10)

input_label = ttk.Label(root, text="Advanced options:", font=('Helvetica', 14))
input_label.pack(pady=5)

button_frame_2 = ttk.Frame(root)
button_frame_2.pack(pady=20)

trim_button = ttk.Button(button_frame_2, text="Trim file", command=trim_audio, bootstyle=INFO, width=16)  # Adjust width here
trim_button.pack(side='left', padx=10)

merge_button = ttk.Button(button_frame_2, text="Merge files", command=merge_audio, bootstyle=INFO, width=16)  # Adjust width here
merge_button.pack(side='left', padx=10)

edit_button = ttk.Button(button_frame_2, text="Edit file info", command=edit_file, bootstyle=INFO, width=16)  # Adjust width here
edit_button.pack(side='left', padx=10)

effects_button = ttk.Button(button_frame_2, text="Audio settings", command=audio_settings, bootstyle=INFO, width=16)  # Adjust width here
effects_button.pack(side='left', padx=10)

extract_button = ttk.Button(button_frame_2, text="Extract from video", command=extract_audio, bootstyle=INFO, width=16)  # Adjust width here
extract_button.pack(side='left', padx=10)

input_label = ttk.Label(root, text="Compressed files:", font=('Helvetica', 14))
input_label.pack(pady=5)

style = ttk.Style()
style.configure('Treeview', font=("Helvetica", 10))

tree_frame = ttk.Frame(root)
tree_frame.pack(pady=10, fill=ttk.BOTH, expand=True)

tree = ttk.Treeview(tree_frame, columns=("Input File", "Output File", "Original Size", "Compressed Size", "Compression (%)"), show='headings', bootstyle=PRIMARY, style='Treeview')
tree.heading("Input File", text="Input File")
tree.column("Input File", anchor=ttk.CENTER)
tree.heading("Output File", text="Output File")
tree.column("Output File", anchor=ttk.CENTER)
tree.heading("Original Size", text="Original Size")
tree.column("Original Size", anchor=ttk.CENTER)
tree.heading("Compressed Size", text="Compressed Size")
tree.column("Compressed Size", anchor=ttk.CENTER)
tree.heading("Compression (%)", text="Compression (%)")
tree.column("Compression (%)", anchor=ttk.CENTER)
tree.pack(fill=ttk.BOTH, expand=True, padx=5)

tree.bind("<Double-1>", play_file)

tree.bind("<Button-3>", on_right_click)

button_frame_3 = ttk.Frame(root)
button_frame_3.pack(pady=20)

clear_button = ttk.Button(button_frame_3, text="Clear History", command=clear_table, bootstyle=DANGER, width=15)
clear_button.pack(side="left",padx=10)

clear_selected_button = ttk.Button(button_frame_3, text="Clear Selected", command=clear_selected_rows, bootstyle=WARNING, width=15)
clear_selected_button.pack(side="left",padx=10)

progress_label = ttk.Label(root, text="", font=('Helvetica', 12))
progress_label.pack(pady=(10, 0))

style = ttk.Style()
style.configure("Transparent.Horizontal.TProgressbar", troughcolor=root.cget('bg'), background=root.cget('bg'), bordercolor=root.cget('bg'))
style.configure("Visible.Horizontal.TProgressbar", troughcolor="lightgray", background="#007bff")

progress_bar = ttk.Progressbar(root, style="Transparent.Horizontal.TProgressbar")
progress_bar.pack(pady=(0, 20))

context_menu = Menu(root, tearoff=0)
context_menu.add_command(label="Additional Info", command=show_additional_info)
context_menu.add_command(label="Show spectogram", command=show_spectogram)

root.bind("<Configure>", update_progress_bar_width)

root.mainloop()