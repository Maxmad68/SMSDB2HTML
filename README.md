# SMSDB2HTML
Archive your sms.db messages database as a iOS like web site

# Installation
To install a full version of SMSDB2HTML, type

    git clone https://github.com/Maxmad68/SMSDB2HTML && cd SMSDB2HTML && sh install.sh && cd .. && rm -rf SMSDB2HTML

Otherwise, you can just download, the Python file, it will download ressources file when executed. (Best way to use SMSDB2HTML if you are not administrator)

# How to use
## Usage
The command syntax is:<br>
  smsdb2html <sms.db> <output dir> [-a <attachments dir> --copy-attachments]<br><br>
   
 - <sms.db> is the path to the messages database (see Archive iOS messages below)<br>
 - <output dir> is the output folder. It will be created by the software, so it mustn't yet exist. It will contains all HTML, CSS and ressources files.<br>
Optional:<br>
 - -a <attachments dir> : attachments dir is the folder containing all attachments. If not specified, pictures, videos and other files won't be shown in the html path.
 - --copy-attachments means the attachments folder will be copied to the output folder. It can be useful if you want your archive to be stored on another disk or access it from another machine. It omitted, the attachments will be local paths, relative to the disk.

## Archive iOS messages


## Archive macOS messages

macOS messages database is stored at:
    
    ~/Library/Messages/chat.db
    
and attachments at:

    ~/Library/Messages/Attachments

macOS chat.db works as well as iOS sms.db. This means you can use smsdb2html to archive macOS messages.<br>
For most cases, this command should work:

    smsdb2html ~/Library/Messages/chat.db outputDir -a ~/Library/Messages/Attachments
