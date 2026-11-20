* 5T OTA
.subckt ota5t VINP VINN VOUT VBIAS VPWR VGND
MP1 VOUT VINN ND VPWR sky130_fd_pr__pfet_01v8 w=4 l=0.5 nf=2
MP2 ND VINP ND VPWR sky130_fd_pr__pfet_01v8 w=4 l=0.5 nf=2
MN1 ND VINP VGND VGND sky130_fd_pr__nfet_01v8 w=2 l=0.5
MN2 VOUT VINN VGND VGND sky130_fd_pr__nfet_01v8 w=2 l=0.5
MN3 ND2 VBIAS VGND VGND sky130_fd_pr__nfet_01v8 w=2 l=0.5
.ends
