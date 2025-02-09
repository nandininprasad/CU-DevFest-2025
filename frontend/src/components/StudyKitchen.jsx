import "../styling/StudyKitchen.css"

function StudyKitchen() {
    return (
    <div class="container">
        <header class="header">
            <div class="logo">Study</div>
            <nav class="navigation">
                <a href="#">Characters</a>
                <a href="#">Games</a>
                <a href="#">Study</a>
                <a href="#">Log</a>
            </nav>
        </header>
        <main class="main-content">
            <div class="content-overlay">
                <h1>Study Kitchen</h1>
                <p>Select from tutoring of Gordon Ramsay, Yeller from bullying from mate your cray to not catastrophe any off the s clots. Lorem ipsum, chef.</p>
                <div class="timer-selection">
                    <div class="timer-option">
                        <input type="radio" id="pomodoro" name="timer" checked/>
                        <label for="pomodoro">Pomodoro Timer</label>
                    </div>
                    <div class="timer-option">
                        <input type="radio" id="custom" name="timer"/>
                        <label for="custom">Custom Timer</label>
                    </div>
                </div>
                <button class="start-button">Start Studying</button>
                <button class="log-button">Daily Log</button>
            </div>
        </main>
        <footer class="footer">
            <p>&copy; StudKitchen.com &nbsp;&nbsp;|&nbsp;&nbsp; <a href="#">Privacy Policy</a> &nbsp;&nbsp;|&nbsp;&nbsp; <a href="#">Terms of Service</a></p>
        </footer>
    </div>
    )
}

export default StudyKitchen;
