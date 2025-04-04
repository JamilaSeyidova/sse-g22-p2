from gui.app import App

def main():
    print("Launching GUI...")
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        print("An error occurred while running the GUI:")
        import traceback
        traceback.print_exc()
    finally:
        print("Exited GUI")

if __name__ == "__main__":
    main()