#!/bin/bash
#crontab -e   #add following to the editor
#@reboot {address of the script}
#chmod +x reboot_script.sh
#sudo service nginx start  || or use 
#sudo systemctl enable nginx.service
cd ~/sang/processing_code
forever start -c "python3 -m streamlit run" "Front End OCBC/chatbot.py"
forever start -c python3 gptv2.py