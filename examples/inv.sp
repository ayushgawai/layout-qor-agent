* inverter SKY130-style
.subckt inv A Y VPWR VGND
MP1 Y A VPWR VPWR sky130_fd_pr__pfet_01v8 w=2 l=0.15 nf=2
MN1 Y A VGND VGND sky130_fd_pr__nfet_01v8 w=1 l=0.15 nf=1
.ends
