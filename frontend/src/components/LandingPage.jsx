import "../styling/LandingPage.css";
import focusTeaImage from "../assets/focus_roast.svg";
import tranquiliteaImage from "../assets/tranquilitea.svg";
import matchaModeImage from "../assets/matcha_mode_white.svg";
import landingpageimage from "../assets/landing_page.svg";
import { Link } from "react-router-dom";


//import image from assets/focus_roast.svg


function LandingPage() {
    return (
        <div>
            <img src={landingpageimage} className="LandingImage" alt="landing_page" />
            <div className="secondpage">
            <div className="Links">
                <div className="FocusRoast">
                    <Link to="/focus-roast">
                        <img src={focusTeaImage} alt="focus_roast" />
                    </Link>
                </div>

                <div className="TranquiliTea">
                    <Link to="/tranquilitea">
                        <img src={tranquiliteaImage} alt="tranqulitea" />
                    </Link>
                </div>
            </div>
            <div className="MatchaMode">
                <img src={matchaModeImage} alt="matcha_mode" />
            </div>
            </div>
        </div>
    );
}

export default LandingPage;