import tkinter as tk
import threading
import requests
import time
import random
import yt_dlp
from tkinter import messagebox, ttk

class VideoWatcherBot:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Watcher Bot")
        self.root.geometry("600x700")
        self.root.configure(bg="#2E2E2E")  # Background color

        self.video_bots = []
        self.video_info = {}
        self.running = True  # To control thread execution

        # Create the GUI components
        self.create_widgets()

        # Bind the close event to handle exit errors
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def create_widgets(self):
        # Title Label
        title_label = tk.Label(self.root, text="YouTube Video Watcher Bot", font=("Arial", 18, "bold"), bg="#2E2E2E", fg="#FFFFFF")
        title_label.pack(pady=10)

        # Video Link Entry
        tk.Label(self.root, text="Enter Video Link:", bg="#2E2E2E", fg="#FFFFFF").pack(pady=5)
        self.video_link_entry = tk.Entry(self.root, width=50, bg="#444444", fg="#FFFFFF", highlightbackground="#555555", highlightcolor="#666666")
        self.video_link_entry.pack(pady=5)

        # Start Time Entry (optional)
        tk.Label(self.root, text="Start Time (MM:SS, optional):", bg="#2E2E2E", fg="#FFFFFF").pack(pady=5)
        self.start_time_entry = tk.Entry(self.root, width=20, bg="#444444", fg="#FFFFFF", highlightbackground="#555555", highlightcolor="#666666")
        self.start_time_entry.pack(pady=5)

        # End Time Entry (optional)
        tk.Label(self.root, text="End Time (MM:SS, optional):", bg="#2E2E2E", fg="#FFFFFF").pack(pady=5)
        self.end_time_entry = tk.Entry(self.root, width=20, bg="#444444", fg="#FFFFFF", highlightbackground="#555555", highlightcolor="#666666")
        self.end_time_entry.pack(pady=5)

        # Number of Views
        tk.Label(self.root, text="Number of Views:", bg="#2E2E2E", fg="#FFFFFF").pack(pady=5)
        self.views_entry = tk.Entry(self.root, width=10, bg="#444444", fg="#FFFFFF", highlightbackground="#555555", highlightcolor="#666666")
        self.views_entry.pack(pady=5)

        # Buttons to Start and Stop the Viewing Bots in a row
        button_frame = tk.Frame(self.root, bg="#2E2E2E")  # Frame for buttons
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start Watching", command=self.start_bots, bg="#28A745", fg="#FFFFFF")
        self.start_button.grid(row=0, column=0, padx=5)  # Button 1

        self.stop_button = tk.Button(button_frame, text="Stop Watching", command=self.stop_bots, state=tk.DISABLED, bg="#DC3545", fg="#FFFFFF")
        self.stop_button.grid(row=0, column=1, padx=5)  # Button 2

        # Output Fields
        self.output_label = tk.Label(self.root, text="Output:", bg="#2E2E2E", fg="#FFFFFF")
        self.output_label.pack(pady=5)
        self.output_text = tk.Text(self.root, height=10, width=70, bg="#333333", fg="#FFFFFF", wrap=tk.WORD)
        self.output_text.pack(pady=5)

        # Scrollbar for output text
        self.scrollbar = tk.Scrollbar(self.root, command=self.output_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=self.scrollbar.set)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient='horizontal', mode='determinate', length=400)
        self.progress.pack(pady=5)

        # Progress Text Label
        self.progress_text_label = tk.Label(self.root, text="Progress: 0%", bg="#2E2E2E", fg="#FFFFFF")
        self.progress_text_label.pack(pady=5)

        # Credits Section
        credits_label = tk.Label(self.root, text="Credits to Developer:", font=("Arial", 12, "bold"), bg="#2E2E2E", fg="#FFFFFF")
        credits_label.pack(pady=10)

        developer_name_label = tk.Label(self.root, text="Naresh Dhanuk", bg="#2E2E2E", fg="#FFD700")  # Gold color for the name
        developer_name_label.pack(pady=5)

        # Optionally, you can add a link or additional info about the developer here.
        additional_info_label = tk.Label(self.root, text="Thank you for using this tool!", bg="#2E2E2E", fg="#FFFFFF")
        additional_info_label.pack(pady=5)

    def start_bots(self):
        video_link = self.video_link_entry.get()
        start_time = self.start_time_entry.get() or "00:00"
        end_time = self.end_time_entry.get()  # Get end time input
        views = self.views_entry.get()

        # Validate input
        if not video_link or not views.isdigit():
            messagebox.showerror("Input Error", "Please fill all fields correctly!")
            return

        self.start_button.config(state=tk.DISABLED)  # Disable start button
        self.stop_button.config(state=tk.NORMAL)  # Enable stop button

        start_seconds = self.convert_to_seconds(start_time)
        end_seconds = None

        if end_time:  # If end time is provided, convert it to seconds
            end_seconds = self.convert_to_seconds(end_time)

        # Create bots and start threads
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Starting {views} viewing bots...\n")
        
        # Reset the progress bar
        self.progress['value'] = 0
        self.progress_text_label.config(text="Progress: 0%")

        for i in range(int(views)):
            bot_thread = threading.Thread(target=self.watch_video, args=(video_link, start_seconds, end_seconds))
            bot_thread.start()
            self.video_bots.append(bot_thread)

    def stop_bots(self):
        """Stop all running bots."""
        self.running = False  # Stop all bots
        self.output_text.insert(tk.END, "Stopping all watching bots...\n")
        
        # No need to join the main thread, just reset the bot list
        self.video_bots.clear()

        self.start_button.config(state=tk.NORMAL)  # Enable start button
        self.stop_button.config(state=tk.DISABLED)  # Disable stop button
        
        # Reset the progress bar
        self.progress['value'] = 0
        self.progress_text_label.config(text="Progress: 0%")

    def watch_video(self, video_link, start_seconds, end_seconds):
        try:
            # Use yt-dlp to get video info
            ydl_opts = {
                'quiet': True,
                'format': 'best',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_link, download=False)
                self.video_info['title'] = info.get('title')
                self.video_info['channel'] = info.get('uploader')
                self.video_info['views'] = info.get('view_count')
                self.video_info['subscribers'] = self.get_channel_subscribers(info['uploader'])
                self.display_video_info()
                
                video_url = info['url']
                total_duration = int(info['duration'])  # Get the actual video length

            # If end_seconds is not provided, use total duration of the video
            if end_seconds is None or end_seconds > total_duration:
                end_seconds = total_duration

            # Simulate watching by streaming or downloading part of the video
            session = requests.Session()
            headers = {'User-Agent': self.generate_user_agent()}
            video_response = session.get(video_url, headers=headers, stream=True)

            # Simulate ad detection
            ad_detected = random.choice([True, False])  # Simulating ad detection
            if ad_detected:
                self.output_text.insert(tk.END, "Ad detected! Waiting for 10 seconds to skip...\n")
                time.sleep(10)  # Simulate waiting for ad to finish
                self.output_text.insert(tk.END, "Ad skipped! Continuing view...\n")

            # Watching progress
            total_seconds = end_seconds - start_seconds
            for watched_seconds in range(total_seconds):
                if not self.running:  # Check if the bot should stop
                    break
                self.progress['value'] = ((watched_seconds + 1) / total_seconds) * 100  # Update progress bar
                self.progress_text_label.config(text=f"Progress: {int((watched_seconds + 1) / total_seconds * 100)}%")  # Update progress text
                time.sleep(1)  # Simulate watching
            
            self.output_text.insert(tk.END, "Finished watching video!\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Error occurred: {str(e)}\n")
        finally:
            self.running = True  # Reset running state for the next bot

    def generate_user_agent(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0.2 Safari/605.1.15",
            "Mozilla/5.0 (Linux; Android 10; Pixel 3 XL Build/QPP1.190502.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Mobile Safari/537.36",
        ]
        return random.choice(user_agents)

    def get_channel_subscribers(self, channel_name):
        # Placeholder for YouTube API logic
        return random.randint(1000, 100000)  # Simulate getting subscriber count

    def display_video_info(self):
        self.output_text.insert(tk.END, f"Video Title: {self.video_info['title']}\n")
        self.output_text.insert(tk.END, f"Channel Name: {self.video_info['channel']}\n")
        self.output_text.insert(tk.END, f"Views: {self.video_info['views']}\n")
        self.output_text.insert(tk.END, f"Subscribers: {self.video_info['subscribers']}\n\n")

    def convert_to_seconds(self, time_str):
        """Convert MM:SS to seconds."""
        if ':' in time_str:
            minutes, seconds = map(int, time_str.split(':'))
            return minutes * 60 + seconds
        return 0

    def on_exit(self):
        """Handle exit events gracefully."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.running = False  # Ensure all bots are stopped
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoWatcherBot(root)
    root.mainloop()
