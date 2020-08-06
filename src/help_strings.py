report_abstract =  \
r"""
<p>This is an automatic report for the Fault Injection on Memory Arrays and Countermeasures Project.</p>
<p><u>Students:</u></p>
<ol>
<ol>Yagel Ashkenazi &amp; David Peled</ol>
</ol>
<p><u>Researchers:</u></p>
<ol>Prof. Osnat Keren | Dr. Yoav Weizman</ol>
<p>The report contains an analysis of clock-glitches attacks done on a chip of the Pacific series. 
The target of the attacks were one of the 11 memory arrays of the chip, which are equipped with a fault-injection detection mechanism.
Detection of faults is done by the various CpC codes implemented in the memory arrays.</p>

<h2>Fault Types</h2>
<p>We attack the chip during writing by inserting a clock glitch.
For better analysis on the faults generated, one should take into account the different types of faults that could happen.
Some faults are caused by technical reasons
of the the system (e.g. skipping an address). 
</p>
<p>
Since we wish to research the attacker's ability to 'mask' (cause a codeword to change to another),
we should filter out such faults since they do not temper with the actual codeword, just move it around. 
</p>
<p>
We make the following distinction between types of faults generated: </p>
<ul>
  <li><u>write deny</u> - memory content remained the same after attempting to write.</li>

  <li><u>write shift</u> - wrote to the wrong address, usually to the original address + offset.</li> 

  <li><u>write-corrupt</u> - Any fault that is not one of the above, hopefully it is a fault where we succesfully corrupted the information written to memory, in contrast to just moving it around.</li>
</ul>

<h2>Attack Parameters</h2>
<p>
  For better understanding of the report structure, we describe how each attack is charecterized.</p>
<p>The attack parameters are: </p>
<ul>
    <li><u>VDD</u> - The system's specification states 1.2V is required.
        Lowering the vdd relaxes the timing constraints, and allows our glitches to become relevant even with the LPFs present in the system.
        <br/>
        There are actually many vdd parameters, since the system vdd signals consist of a triplet:
        <ul>
            <li><u>cpc_vdd</u> - supplied to the memory array.</li>
            <li><u>vddcore</u> - supplied to the pacific controller/bist/core.</li>
        </ul>
        As of today, for each attack we are always guaranteed that cpc_vdd=vddcore=cpc_vddr.
    </li>

    <li><u>delay</u> - glitch's offset relative to the clock rising edge</li>
    <li><u>height</u> - glitch's amplitude, positive when we inject when clk is low.</li>
    <li><u>index</u> - clock cycle at which we inject the glitch </li>

    <li><u>pulse-width</u> - The width of the pulse </li>
    <li><u>cycles</u> - number of consecutive repeated pulses </li>
    <li><u>pulse-freq</u> - Frequency of repeated pulses </li>
</ul>

<h2> Report Strucure </h2>
<p>
At first, we give a general analysis of the attacks. 
We look for attack parameters that generate write-corrupt faults,
and see how the number of bit-flips is affected by different parameters.
</p>
<p>
Afterwards, we limit our analysis to a specific "set" of attacks and see how the errors behave.
For example, we could define a "set" as all the attacks with height=1.2v, and delay=0.5ns.
A "set" can be defined in many ways, we anaylyze sets that:
</p>

<ul>
    <li>
        Tested thoroughly
        sets that have few attacks in them don't have enough statistical data.
    </li>
    <li>
        Have a high yield of write-corrupt faults
        sets that produced a few faults cannot be used to draw meaningful conclusions.
    </li>
</ul>

As a final note, all the graphs are interactive - using the small tooltip at the bottom-left corner one can move and zoom freely.
The home button restores the original zoom settings.
"""
#codstr=str(CPC[cpc])  < This should print n, k, r and the ground robust codes used and their parameters.

report_cpc = \
r"""
<p>In this report, we focus on attacks on the CpC{cpc} memory array: 
</p>
<p>
{codestr}
</p>
"""

technical_info = \
r"""
For list of logs used in this report and other technical information, see bottom of the page. <br/>
Attacks done with the {awg}. <br/>
Report generated on {date}. <br/>
"""


general_report_abstract = \
r"""
In this section we try to give an answer to two questions: <br/>
<ul>
    <li>
    How should an attacker configure the clock glitches to produce write-corrupt faults? <br/>
    </li>
    <li>
    How do bitflips behave accross different parameters? <br/>
    </li>
</ul>
"""

general_report_vdd = \
r"""
For each vdd, what is the marginal probability of generating a write-corrupt fault? <br/>
"""
general_report_statistics = \
r"""
In this section, we present a statistical analysis across all attacks.
This gives us insight into what kind of fault types are present and how the CpC code handled them.
"""

general_report_foreach_vdd = \
r"""
To find good attacks, we want to look into more parameters where a specific vdd is given.
"""

specific_report_abstract = \
r"""
In this section we provide statistical analysis of attacks which belong to the same "set". <br/>
For example, a set might be defined by the width of the glitch, it's relative position to the clock and so on. <br/>
In the table below the analyzed sets and more are given. <br/>

We treat each attack as a unique instance of the "attack-set", and try to provide insight on the behavior of the set as a whole: <br/>
<ul>
    <li> How do the faults behave? </li>
    <li> Were we able to achieve masking? </li>
    <li> Do bit flips behave like BSC? </li>
</ul>
When reviewing the following graphs with the x-axis 'bit', keep in mind that the rightest r={r} bits are the redundancy bits.
"""


colorfulness_abstract = \
"""
Our statistical tests assumes the data is distributed uniformly. </br>
In this heatmaps we see the P(data=1) in the read and write data, as funcion of address and bit location. </br>
Ideally, P is around 0.5 at all points.
"""

numbitflips_bit_heatmap_abstract = \
"""
The following heatmap shows the relation between the number of bitflips and where those flips occured.
"""

index_hist_abstract = \
"""
<u>index</u> is the parameter resposible for the clock cycle we attack. We want to attack all the cycles.<br/>
The following graph shows the number of tries we did on every 0 < index < 100
"""

error_behave_abstract = \
"""
We want to have a better understanding of the behavior of errors.
<br/>
At first, we want to know how the number of bit flips is distributed:
"""

index_address_heatmap_abstract = \
"""
We start by justifying our analyses. We do some sanity checks, and check the colorfulness of our data.<br/> <br/>
Write to memory is sequential. Hence we expect that write-corrupt faults happens in address equal to index (or greater, at least)
<br/>
The following heatmap tries to visualise this relation.
"""

heatmap_bitflips_address_abstract = \
"""
Is the nubmer of bitflips independent of the address?
"""