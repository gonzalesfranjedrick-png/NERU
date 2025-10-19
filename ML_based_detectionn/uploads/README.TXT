Error information to be written hereIR RELIEF v2.2 ##
     Data Entry and Validation modules for Summary List of Sales and Purchases (SLSP)
                                       (c)2002


WHAT IS RELIEF?
  RELIEF stands for the Reconciliation of Listings for Enforcement. The RELIEF System is a
  tool created by the Philippine's Bureau of Internal Revenue to capture the monthly summary
  of sales, purchases and importations required to be submitted by VAT-registered taxpayers
  on a quarterly basis in magnetic form based on a prescribed electronic format. The
  consolidation and matching of information with other externally sourced data will 
  detect underdeclaration of revenues/overdeclaration of expenses resulting in greater tax
  potential.

PC REQUIREMENTS
  It needs a PC with at least:
  - Pentium I - 166 mHz processor or higher
  - 32mb RAM
  - SVGA monitor capable of at least 800x600 or 1024x768 resolution
  - Windows 95 operating system (Windows 98 recommended)

MAIN FEATURES 
  - Data maintenance of Sales, Purchases and Importations
  - Data import / export capability across multiple PCs
  - Purging and Archiving facility
  - Database back-up and recovery facility
  - Reports generation

VERSION HISTORY
	
	Version 2.3
  - accepts 400 - 800 TIN Series (Taxpayer Information Window)
  - inclusion of RDO 127 LARGE TAXPAYERS DISTRICT OFFICE - DAVAO in the list
	

	Version 2.2
  - accepts 500 - 800 TIN Series

	Version 2.1
  - FTP fixes
  - Added new RDO
  - Fix validations

	Version 2.0
  - Clean Special Character
  - Unarchived Utility
  - Relaxable 12% computation of output tax

	Version 1.2
  - Import / Export capability across multiple PCs
  - Editable VAT
  - Report Preview
  - Printing Option
  - Chronological Order for entries at Importation (Import Entry No. or Assessment Date)
  - Alphabetical Order for generated Sales and Purchases entries
  - Gross Taxable field included in the Sales and Purchases
  - Relaxable 10% computation of output tax
  - Folder / directory names with spaces acceptable in Validation 

	Version 1.0
  - Initial release

INSTALLATION PROCEDURE
  Note: Prior to installation of the program, it is recommended to close all active 
	applications (i.e. Office Shortcut Bar)to avoid conflicts on sharing of dll 
	files with other Microsoft applications.

  Using the 4 diskettes - After inserting the Disk 1 of the RELIEF installer in your floppy
	drive, select RUN from the Taskbar Start Menu then type A:\SETUP.EXE, press the
	Enter key and follow the prompts. The installed components will be located in a 
	folder called bir_rlf in your computer's root directory (for example: C:).
 
  Using the downloaded file from the web - Execute (double-click) the file downloaded from 
	the web to install or update an existing copy :
	- relief_VX.X.exe - Full installer with release version <X.X>

ACTIVATION / USAGE
  You can access the RELIEF Data Entry System and Validation modules via the BIR Relief
  folder in your Programs menu. If you want to create shortcuts on your desktop for the Data
  Entry and Validation modules, locate the 'BIRRLF.EXE' and 'VALRLF.EXE' files found inside 
  BIR_RLF folder.

FREQUENTLY ASKED QUESTIONS
  Q1. What is needed to resolve errors occurring during the usage of the system?
  A1. Make sure that there is only one session of RELIEF active at all times. Close all
	RELIEF sessions and re-activate again.
  A1. Make sure that a clean copy of the installer disk is in hand. Get the latest copy from
	a nearest RDO or RDC or download from the BIR website at www.bir.gov.ph.

  Q2. Is it possible to use the system for more than one company in a single pc?
	(For accounting and law firms taking charge of transactions of numerous companies.)
  A2. Yes. Create new folder/s in your root directory. Rename the folder/s with the company
	name for identification purposes. Copy all the contents of the folder BIR_RLF and
	paste into each of the newly created folders. Then create shortcuts for the
	BIRRLF.EXE file found in each folder and paste them to your desktop. It is also
	recommended to rename these files affixing them with the name of the company
	(for example: ABC_company_DataEntry). Make sure that Owner Information are 
	changed/updated for newly created folders.

  Q3. How can the user resolve the error "The Input Tax/Output Tax must be equivalent to
	10% of the transaction" that occurs during validation?
  A3. If this is the only error, the user could ignore this error and proceed to submitting
	the summary lists since the RDO has the updated validation module. The user could 
	also request for a copy of the URLFVALID.EXE file from the RDO to update their
	RELIEF Validation module. They only need to decompress the file in the root
	directory of their PC.

  Q4. What is the prescribed screen resolution for the user to view all available 
	options/buttons after selecting a type of transaction?
  A4. Check the settings of the screen display(desktop) by going to the Control Panel then
	go to Display and adjust the screen setting to 800x600 or 1024x768 resolution.

  Q5. Can the user submit their summary list using their own extract program?
  A5. The user may use their own extract program provided that their system has the ability
	to convert the database files into comma delimited text files. Have their IT
	department develop a script within their database program to do this. Please refer
	to the prescribed templates / file formats available at RDO or they can download the
	technical annexes from the BIR website.         
  A5. User can also submit using the excel format as long as it conforms with the BIR file
	format under RMC 24-2002. Ask their RDO for a copy of the Excel templates for their
	guidance.

  Q6. Where can the users get the RELIEF installer, technical annexes and job-aids?
  A6. They can get copies from the RDO or RDC.
  A6. If they have access to the internet, access the BIR webpage then go to BIR FORMS.
	Click on the 2550Q form to go to the location of the downloadable installers, 
	annexes and job-aids.

  Q7. How can the user successfully validate a generated file (.DAT) if upon clicking the
	Validate File button, a BIR System Message stating "Command contains unrecognized
	phrase/keyword. Error Number: 36" appeared?
  A7. The user must make sure that the generated file is not located inside a folder where
	the foldername contain spaces. User can rename the folder wherein blank spaces are
	replaced with underscores.
  A7. The user can get the update patch from your RDO or from the web to update their
	Validation module.

  Q8. Is the RELIEF program free of charge?
  A8. Yes.

  Q9. How will the user remove or uninstall the RELIEF program from the computer?
  A9. Select RUN from the Taskbar Start Menu then type C:\BIR_RLF\SETUP\SETUP.EXE, press the
	Enter key and follow the prompts.

  Q10. For users who will submit using the Excel format, what is the prescribed formula for
	computations? Users always encounter the "Header not equal to total details." error
	during validation.
  A10. All computations in the Excel format must be rounded off to the nearest 2 decimal
	places. (for example: L3=J3*K3 - it must be L3=round(J3*K3,2))

  Q11. In case of detailed explanations for questions, where can the user seek help?
  A11. User can get in touch with the BIR Contact Center at 9818888 or email at 
       contact_us@cctr.bir.gov.ph or Taxpayer Service Section of their RDO or contact the 
       BIR Helpdesk at 926-9630, 981-7050 to 51, 925-2015-17 or email at hdeskno@bir.gov.ph.

  Q12. Can I import data from a previous version of RELIEF Data Entry and Validation Module?
  A12. Yes, by completing the following steps:

                Note: Make sure that the NEW version of RELIEF has not been encoded with data. 

	1.	Create a backup of the PREVIOUS version of RELIEF.
		a.	Locate the program/directory where the PREVIOUS version of RELIEF is installed.
		b.	Click RELIEF Database Backup (or dbutility.exe). The Database Utility window appears.
		c.	Click Backup. The Select Directory window appears.
		d.	Click Select to accept the default folder location. A system message appears, indicating the directory where the backup file is stored. Please note it down as you will need it to perform Step 2e. 
		e.	Click OK. The Database Utility window appears.
		f.	Click Quit to exit the application.

	2.	Restore backup using the NEW version of RELIEF.
		a.	Locate the program/directory where the NEW version of RELIEF is installed.
		b.	Click RELIEF Database Backup (or dbutility.exe). The Database Utility window appears.
		c.	Click Recover. A warning message appears, asking you whether or not to replace the database. 
		d.	Click Yes. The Select Directory window appears.
		e.	Locate the directory where the backup file is stored. Click Select. A message indicating that the database was restored appears on your screen.
		f.	Click OK. The Database Utility window appears.
		g.	Click Quit to exit the application.



END OF FILE

- vte -