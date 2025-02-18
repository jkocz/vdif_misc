import casperfpga

#connect to the fpga
fpga = casperfpga.CasperFpga('fpga_ip_address',transport=casperfpga.KatcpTransport)

# program the fpga
fpga.upload_to_ram_and_program('fpg_filename.fpg')

# read the register and other system information
fpga.get_system_infromation('fpg_filename.fpg')

# connect to the rfdc block
rfdc_fpga = fpga.adcs['rfdc']
rfdc_fpga.init()

# if you have not previously uploaded the clock files
# (these files only need to be uploaded once)
rfdc_fpga.upload_clk_file('rfsoc4x2_lmx_inputref_256M_outputref_512M.txt')
rfdc_fpga.upload_clk_file('rfsoc4x2_lmk_CLKin0_extref_5M_PL_128M_LMXREF_256M.txt')

# get a list of the clock files on the board
c = rfdc_fpga.show_clk_files()

# program the LMK, do this twice
rfdc_fpga.progpll('lmk',c[index_of_lmk_file])
rfdc_fpga.progpll('lmk',c[index_of_lmk_file])
# program the LMK
rfdc_fpga.progpll('lmx',c[index_of_lmx_file])
# (The LMK and LMX clocks can be chagned to a different default startup by editing the user contab on the RFSoC)


#check the status of the ADCs
#ADCs 0 and 2 should be in state 15, PLL: 1
rfdc_fpga.status()

# reset the 100gb interface
fpga.write_int('pkt_rst',3)
fpga.write_int('pkt_rst',0)

# initialise the network parameters
fabric_port= 4000
mac_base= (2<<40) + (2<<32)
ip_base = 192*(2**24) + 168*(2**16) + 100*(2**8)

tx_core_name = 'onehundred_gbe'
gbe_tx = fpga.gbes[tx_core_name]

# the arp table will not auto populate. This initialised it with some base set of values
gbe_tx.set_arp_table(mac_base+numpy.arange(256))
# use set_single_arp_entry to define known send and receive addresses.
# this is the receiving nic. Replace the IP and MAC address with the local values.
gbe_tx.set_single_arp_entry('192.168.100.101',0x0123456789ab)
# this is the FPGA. Replace the IP address with the local value
gbe_tx.set_single_arp_entry('192.168.100.20',mac_base+20)
# finish configuratin the FPGA 100Gb block
gbe_tx.configure_core(mac_base+20,ip_base+20,fabric_port)

# set destination addresseso
# inp1 corresponds to the inputs from ADC4 on the FPGA board. 
# The IP and PORT here should be the DESTINATION IP and Port.
fpga.write_int('inp1_ip',ip_base+101)
fpga.write_int('inp1_port',fabric_port+1)
# inp2 corresponds to the inputs from ADC2 on the FPGA board.
# The IP and PORT should again be configured to the DESTINATION IP and Port
fpga.write_int('inp2_ip',ip_base+101)
fpga.write_int('inp2_port',fabric_port+1)
# Set a different thread number for inp2 if desired.
fpga.write_int('inp2_th_id',1)

## Other header parameters can be set here:
# Reference Epoch: ref_epoch
# Seconds from Epoch: sec_from_ep
# Thread ID: th_id
# Station ID: st_id
# Num channels: num_ch
# VDIF version number: ver
# EDV: edv
# Extended user data (1): eud24
# Extended user data (2): eud32_1
# Extended user data (3): eud32_2
# Extended user data (4): eud32_3


# load seconds from epoch and start data transmission
fpga.write_int('arm',1)

