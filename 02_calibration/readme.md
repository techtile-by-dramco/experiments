The problem of calibration, and more specifically reciprocity calibration, encompasses all procedures to allow to estimate the DL channel (for the CSPs to the user) from the UL channel (from the user to the CSPs).

# What is the problem?

A challenge in the Techtile testbed is that the utilized software-defined radios uses two PLLs to up- and downconvert the RF signals. This results in an unknown, but coherent phase difference between the TX and RX PLL, i.e., the phase difference changes with every re-tuning but stays fixed afterwards.
Exploiting reciprocity thus requires us to remove this phase ambiguity from the RX and TX chains in each CSP.

A well-written paper discussing this problem of different phases at the RX and TX chains is discussed in [1]. The author, however, considers a single PLL for the TX and RX chain, meaning that only the sign of the phase is different between TX and RX, while in our case there is also a phase difference (see the appendix for a more general transmission chain).
Nonetheless, I highly suggest reading this letter to demonstrate the difficulties of calibration, which is often wrongly assumed in the literature. 

> insert picture

Adopting the figure and expressions from [1], the effect of the TX ($t_i$) and RX ($r_i$) chains can be written as (ignoring the HW component effects):

$$t_i(f) = e^{+j\phi_t}  e^{-2 \pi f \tau_t}$$

$$r_i(f) = e^{-j\phi_r}  e^{+2 \pi f \tau_r}$$

Given that our clocks are derived from the same clock reference (our NI Octoclocks), 

$$\phi_t = \phi_i + \Delta\phi_t$$

$$\phi_r = \phi_i + \Delta\phi_r$$

The same applies to the time delays $\tau_t$. As detailed above $\Delta\phi$ will be fixed as long as the chains are not re-tuned. As all LO clocks are derived from the same common reference clock, we expect $\phi_i$ to be stable over the experiment and thus only one calibration is necessary to estimate $t_i(f)$ and $r_i(f)$.


# How to do reciprocity calibration
Our approach considers a global reciprocity calibration technique. This is in contrast to [1] which proposes a relative technique which requires all CSPs to know their calibration factor relative to one CSP.
The problem with this approach is that it scales with the number of CSPs. Our approach uses dedicated PLLs available at each CSP to provide a common clock reference, simplifying the calibration procedure, as now all CSPs can calibrate relative to this clock and no signals need to be exchanged between all CSPs.

## Setup

> insert picture


## Procedure

1. In the loopback procedure the phase difference between the RX and TX RF chains is determined, i.e., $\Delta\phi_i$
2. Absolute calibration retrieves the phase difference between the global ref clock and the RX PLL per CSP, i.e., $\phi_{i,r}$
3. The phase received by the CSP coming from the user is determined with reference to the RX PLL of that CSP to estimate the channel state information, i.e.,  $\phi_{i,ch}$. 

### 1. Loopback

A loopback is provided between the RX and TX chains on each CSP. 

A. Transmit the PLL carrier (without any precoding)
B. Receive the TX-PLL at the RX
C. Determine the relative phase differences between the two PLLs, i.e., $\Delta\phi_i$

#### A. Transmit the PLL carrier

To transmit the PLL carrier a real-valued sample is being transmitted (0.8). This means that the I component is 0.8, while the Q is 0.
In essence, we transmit $\cos(2 \pi f t + \phi_{i,t})$. We omit the amplitude term as this won't change the calibration phase.

#### B. Receive the TX-PLL at the RX
At the receiver, we receive the TX-PLL carrier including the TX and RX chain effects (omitting the effect of the cable). Writing this in complex notation:

$$s_{rx}(f) = t_i(f) *  r_i(f)$$

Neglecting the time delays originating from the DACs/ADCs, this can be rewritten as:

$$s_{i,rx}(f) = e^{+j\phi_{i,t}} *  e^{-j\phi_{i,r}}$$

#### C. Relative phase differences between the two PLLs 

$$ \Delta\phi_i = \phi_{i,t} - \phi_{i,r} $$

We thus now know the relative phase difference between the RX and TX PLLs on the same CSP.

### 2. Absolute calibration

Instead of computing the relative calibration terms as done in most works, here we use dedicated PLLs having the same phase over all CSPs. This is done through **TODO provide a link**.
As we distribute a global reference clock to all CSPs, we will define this clock as having zero phase, i.e., everything is relative to this clock.

The received signal from this PLL at CSP $i$ we obtain the relative phase difference between the ref PLL and the RX PLL, i.e., $e^{-j\phi_r}$.

### 3. Reciprocity-based operation

To estimate the channel $H_i=e^{j \phi_{i,ch}}$ between the user and CSP $i$

$s_{i, rx} = $
$\underbrace{e^{2j \pi f t + \phi_{UE}}}_{\text{TX signal}}$ 

$\underbrace{e^{j \phi_{i,ch}}}_{\text{Channel}}$ 

$\underbrace{e^{-j\phi_{i,r}}e^{+2 \pi f \tau_{i,r}}}_{\text{RX chain}}$


 $$ e^{2 \pi f t + \phi_{UE}} e^{j \phi_{i,ch}} e^{-j\phi_{i,r}}e^{+2 \pi f \tau_{i,r}} $$


Given that $\phi_{UE}$ is independent of the CSP, we can discard this term as long as all CSPs have this same unknown but common phase rotation.
We are now looking for a phase rotation ($phi_{i,\text{coh}}$) to precode the transmit signal from each CSP in order to coherently combine all signals at the UE.

What we want at the UE: $e^{-2j \pi f t}  e^{phi_{\text{fixed}}}$
This requires us to transmit a signal cancelling out the phase rotations of the PLLs and the channel.

$$ e^{phi_{\text{fixed}}} = e^{phi_{i,\text{coh}}} e^{j \phi_{i,ch}} e^{+j\phi_t}$$



$$ e^{phi_{i,\text{coh}}} = e^{phi_{\text{fixed}}} e^{-j\phi_t} e^{-j \phi_{i,ch}}$$


What do we know:
- (1) $e^{j\phi_{i,1}} = e^{\phi_{i,t}} e^{-\phi_{i,r}}$ (loopback)
- (2) $e^{j\phi_{i,2}} = e^{-j\phi_{i,r}}$ (abs. PLL calibration)
- (3) $e^{j\phi_{i,3}} = e^{j\phi_{UE}} e^{j \phi_{i,ch}} e^{-j\phi_{i,r}}$ (received UL signal)

Discarting everything that is fixed, this becomes:

$$ e^{phi_{i,\text{coh}}} = e^{-j\phi_{i,1}} e^{j2\phi_{i,2}} $e^{-j\phi_{i,3}}$$

---

$$ \phi_{i,\text{coh}} = -\phi_{i,1} + 2\phi_{i,2} -\phi_{i,3} $$

---


[1]:  Nissel, Ronald. "Correctly Modeling TX and RX Chain in (Distributed) Massive MIMO—New Fundamental Insights on Coherency." IEEE Communications Letters 26.10 (2022): 2465-2469. https://arxiv.org/abs/2206.14752

