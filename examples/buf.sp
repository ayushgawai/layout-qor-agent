.subckt buf A Y VPWR VGND
MP1 N A VPWR VPWR sky130_fd_pr__pfet_01v8 w=2 l=0.15
MN1 N A VGND VGND sky130_fd_pr__nfet_01v8 w=1 l=0.15
MP2 Y N VPWR VPWR sky130_fd_pr__pfet_01v8 w=4 l=0.15 nf=2
MN2 Y N VGND VGND sky130_fd_pr__nfet_01v8 w=2 l=0.15 nf=2
.ends
