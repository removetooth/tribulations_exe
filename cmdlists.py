import prize_cmds

# TODO: Maybe split each command into its own file?
# That way you could auto-generate the command list using
# glob and __import__('keyword').command
# (you could bundle conf, help, and aliases with it too
# if provided, and have a misc confs folder)

# List of functions to run for a given keyword.
cmdList = {
	"transfer": prize_cmds.cmdTRANSFER,
	"nuke": prize_cmds.cmdNUKE,
	"eliminate": prize_cmds.cmdELIMINATE,
	"revive": prize_cmds.cmdREVIVE,
	"peek": prize_cmds.cmdPEEK,
	"timeout": prize_cmds.cmdTIMEOUT,
	"sabotage": prize_cmds.cmdSABOTAGE,
	"bias": prize_cmds.cmdBIAS,
	"fraud": prize_cmds.cmdFRAUD,
	"escape": prize_cmds.cmdESCAPE,
	"thief": prize_cmds.cmdTHIEF,
	"swap": prize_cmds.cmdSWAP,
	"immunity": prize_cmds.cmdIMMUNITY
}
# List of functions to run when accepting a pending confirmation.
confList = {
	"transfer": prize_cmds.confTRANSFER,
	"nuke": prize_cmds.confNUKE,
	"friendlynuke": prize_cmds.confFRIENDLYNUKE,
	"nukemyownteamforrealsies": prize_cmds.confREALLYFRIENDLYNUKE,
	"eliminate": prize_cmds.confELIMINATE,
	"revive": prize_cmds.confREVIVE,
	"peek": prize_cmds.confPEEK,
	"timeout": prize_cmds.confTIMEOUT,
	"sabotage": prize_cmds.confSABOTAGE,
	"bias": prize_cmds.confBIAS,
	"fraud": prize_cmds.confFRAUD,
	"escape": prize_cmds.confESCAPE,
	"thief": prize_cmds.confTHIEF,
	"immunity": prize_cmds.confIMMUNITY
}