.subckt and2 A B Y VPWR VGND
MP1 N A VPWR VPWR sky130_fd_pr__pfet_01v8 w=2 l=0.15
MP2 N B VPWR VPWR sky130_fd_pr__pfet_01v8 w=2 l=0.15
MN1 N A MID VGND sky130_fd_pr__nfet_01v8 w=1 l=0.15
MN2 MID B VGND VGND sky130_fd_pr__nfet_01v8 w=1 l=0.15
MP3 Y N VPWR VPWR sky130_fd_pr__pfet_01v8 w=2 l=0.15
MN3 Y N VGND VGND sky130_fd_pr__nfet_01v8 w=1 l=0.15
.ends
