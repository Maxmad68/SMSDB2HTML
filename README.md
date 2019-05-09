# SMSDB2HTML
Archive your sms.db messages database as a iOS like designed web site.<br>
It supports text messages (SMS and iMessages), MMS, pictures and videos, files attachments, vocal messages, GIFs and Animojis/Memojis

![Chat selector](http://madrau.fr/SMSDB2HTML-Github/screen1.png)<br>
![Messages](http://madrau.fr/SMSDB2HTML-Github/screen2.png)<br>

# Installation
To install a full version of SMSDB2HTML, type

    git clone https://github.com/Maxmad68/SMSDB2HTML && cd SMSDB2HTML && sh install.sh && cd .. && rm -rf SMSDB2HTML

Otherwise, you can just download, the Python file, it will download ressources file when executed. (Best way to use SMSDB2HTML if you are not administrator)

# How to use
## Usage
The command syntax is:<br>
  smsdb2html \<sms.db> \<output dir> [-a \<attachments dir> --copy-attachments]<br><br>
   
 - \<sms.db> is the path to the messages database (see Archive iOS messages below)<br>
 - \<output dir> is the output folder. It will be created by the software, so it mustn't yet exist. It will contains all HTML, CSS and ressources files.<br>
Optional:<br>
 - -a \<attachments dir> : attachments dir is the folder containing all attachments. If not specified, pictures, videos and other files won't be shown in the html path.
 - --copy-attachments means the attachments folder will be copied to the output folder. It can be useful if you want your archive to be stored on another disk or access it from another machine. It omitted, the attachments will be local paths, relative to the disk.

## Archive iOS messages

To use smsdb2html to archive iOS messages, we need to retrieve the sms.db file.
Several options are possible:

#### iOS Backups

The sms.db file has the hash: 3d0d7e5fb2ce288813306e4d4636395e047a3d28.<br>
So, it will be stored at \<Backup>/3d/3d0d7e5fb2ce288813306e4d4636395e047a3d28<br><br>
    
Otherwise, you can use my iOS backup utility [iBake](https://github.com/Maxmad68/iBake) in order to make it easier.
You can retrieve the sms.db file with this command:

    ibake extract <Backup-ID> ~/sms.db -d HomeDomain -f Library/SMS/sms.db

or extract all HomeDomain (sms.db and attachments) with this one:

    ibake extract <Backup-ID> ~/ExtractedHomeDomain -d HomeDomain
  
#### iPhone Filesystem

If the device is jailbroken, or if you can access the iOS root filesystem, you will find the messages directory at this location:

    /private/var/mobile/Library/SMS/

The sms.db and attachments folder are located at:

    /private/var/mobile/Library/SMS/sms.db
    
    /private/var/mobile/Library/SMS/Attachments/


You can copy those files to your computer using SSH, SFTP, or [iFuse](https://github.com/libimobiledevice/ifuse) and then use smsdb2html to archive the conversation.

## Archive macOS messages

macOS messages database is stored at:
    
    ~/Library/Messages/chat.db
    
and attachments at:

    ~/Library/Messages/Attachments

macOS chat.db works as well as iOS sms.db. This means you can use smsdb2html to archive macOS messages.<br>
For most cases, this command should work:

    smsdb2html ~/Library/Messages/chat.db outputDir -a ~/Library/Messages/Attachments
    

