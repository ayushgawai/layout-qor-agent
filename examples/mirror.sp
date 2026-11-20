.subckt mirror IREF IOUT VPWR VGND
MP1 IREF IREF VPWR VPWR sky130_fd_pr__pfet_01v8 w=4 l=0.5 nf=2
MP2 IOUT IREF VPWR VPWR sky130_fd_pr__pfet_01v8 w=4 l=0.5 nf=2
MN1 IREF IREF VGND VGND sky130_fd_pr__nfet_01v8 w=2 l=0.5
.ends
