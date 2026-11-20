.subckt nand2 A B Y VPWR VGND
MP1 Y A VPWR VPWR sky130_fd_pr__pfet_01v8 w=2 l=0.15
MP2 Y B VPWR VPWR sky130_fd_pr__pfet_01v8 w=2 l=0.15
MN1 Y A MID VGND sky130_fd_pr__nfet_01v8 w=1 l=0.15
MN2 MID B VGND VGND sky130_fd_pr__nfet_01v8 w=1 l=0.15
.ends
