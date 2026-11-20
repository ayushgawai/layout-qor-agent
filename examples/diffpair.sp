.subckt diffpair INP INN OUTP OUTN VBIAS VPWR VGND
MN1 OUTP INP TAIL VGND sky130_fd_pr__nfet_01v8 w=3 l=0.5 nf=2
MN2 OUTN INN TAIL VGND sky130_fd_pr__nfet_01v8 w=3 l=0.5 nf=2
MN3 TAIL VBIAS VGND VGND sky130_fd_pr__nfet_01v8 w=2 l=0.5
MP1 OUTP OUTP VPWR VPWR sky130_fd_pr__pfet_01v8 w=3 l=0.5
MP2 OUTN OUTP VPWR VPWR sky130_fd_pr__pfet_01v8 w=3 l=0.5
.ends
