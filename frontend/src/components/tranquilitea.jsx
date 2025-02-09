    import React, { useEffect } from 'react';
    import dreamJournalImage from '../assets/dream_journal.svg';
    import traquiliteaBackground from '../assets/tranquility_landing.svg';
    

    function Tranquilitea() {
        


        
        // window.location.assign("http://localhost:8502");

        return (
            <div className="TranquiliteaMain">
                <img src={traquiliteaBackground} className="TranquiliteaBackground" alt="tranquilitea_background" />
                
                            <img src={dreamJournalImage} className="DreamJournalImage" id="dream-journal-img" alt="dream_journal" />
                            <div className='Fatty' style={{padding: '10px', textAlign: 'center'}} onClick={() => window.location.assign("http://localhost:8502")}>
                    </div>            

                    
                
            </div>
        );
    }

    export default Tranquilitea;