# Implemented equations

All RANK variables are log deviations from the zero-inflation steady state.
Expectation notation is represented by SSJ leads, for example `pi_p(+1)`.

## 1. RBC

The RBC model is the official three-block SSJ example:

1. Competitive firm

   \[
   Y_t=Z_tK_{t-1}^{\alpha}L_t^{1-\alpha},\quad
   r_t=\alpha Z_t(K_{t-1}/L_t)^{\alpha-1}-\delta,\quad
   w_t=(1-\alpha)Z_t(K_{t-1}/L_t)^\alpha.
   \]

2. Household labor supply and capital accumulation

   \[
   C_t=\left(\frac{w_t}{\chi L_t^{\phi}}\right)^{1/\sigma},
   \qquad I_t=K_t-(1-\delta)K_{t-1}.
   \]

   This uses Galí-style preference notation: `sigma` is inverse EIS,
   `phi` is inverse Frisch elasticity, and `chi` is the labor-disutility weight.

3. Goods clearing and Euler equation

   \[
   Y_t-C_t-I_t=0,\qquad
   C_t^{-\sigma}=\beta(1+r_{t+1})C_{t+1}^{-\sigma}.
   \]

## 2. Price-rigidity RANK core

This is Galí Chapter 3. There is no capital accumulation and wages are flexible.
Let `x` be the output gap, `a` technology, `z` the preference/discount-rate
shock, and `nu` the monetary-policy shock.

Natural allocation:

\[
\psi_{ya}=\frac{1+\phi}{\sigma(1-\alpha)+\phi+\alpha},\quad
y_t^n=\psi_{ya}a_t,
\]

\[
r_t^n=-\sigma\psi_{ya}(1-\rho_a)a_t+(1-\rho_z)z_t,
\qquad y_t=x_t+y_t^n.
\]

Dynamic IS equation:

\[
x_t=E_tx_{t+1}-\frac{1}{\sigma}
  \left(i_t-E_t\pi^p_{t+1}-r_t^n\right).
\]

Taylor rule:

\[
i_t=\phi_\pi\pi_t^p+\phi_y y_t+\nu_t.
\]

For transparency the marginal-cost gap is calculated from household and firm
conditions before entering either price cartridge:

\[
n_t=\frac{y_t-a_t}{1-\alpha},\quad
\widehat{mrs}_t=\sigma y_t+\phi n_t,\quad
\widehat{mpl}_t=a_t-\alpha n_t,
\]

\[
\widehat{mc}_t=\widehat{mrs}_t-\widehat{mpl}_t
  =\left[\sigma+\frac{\phi+\alpha}{1-\alpha}\right]x_t.
\]

### Calvo price cartridge

\[
\pi_t^p=\beta E_t\pi_{t+1}^p+\lambda_p^{C}\widehat{mc}_t,
\]

\[
\lambda_p^{C}=\frac{(1-\theta_p)(1-\beta\theta_p)}{\theta_p}
\frac{1-\alpha}{1-\alpha+\alpha\epsilon_p}.
\]

### Rotemberg price cartridge

Under the documented adjustment-cost normalization,

\[
\pi_t^p=\beta E_t\pi_{t+1}^p+\lambda_p^{R}\widehat{mc}_t,
\qquad
\lambda_p^{R}=\frac{\epsilon_p-1}{\psi_p}.
\]

The default `psi_p` is chosen so that `lambda_p^R=lambda_p^C`. The two price
blocks therefore produce identical first-order dynamics at the reference
calibration. Moving `psi_p` is an explicit change in the Phillips-curve slope.

## 3. Wage-rigidity comparison core

These models follow Dennery's comparison and assume flexible goods prices.

### Why there is no separate dynamic IS equation

The household Euler equation has **not** been dropped. Before imposing the
wage-model equilibrium conditions, its log-linear gap form is

\[
\sigma(c_t-E_tc_{t+1})
=-(i_t-E_t\pi^p_{t+1}-r_t^n).
\]

In the sticky-price RANK models, this remains a separate dynamic IS equation
because the output gap and price inflation are independent endogenous
variables. The sticky-wage comparison instead has flexible goods prices, no
capital or government spending, and

\[
c_t=y_t=(1-\alpha)l_t.
\]

Moreover, expected real-wage growth satisfies

\[
E_t\Delta(w-p)_{t+1}=E_t(\pi^w_{t+1}-\pi^p_{t+1}).
\]

This identity and the relevant intratemporal real-wage condition let us
substitute consumption, output, and price inflation out of the Euler equation.
The resulting forward-looking condition is written directly in labor and wage
inflation. It is the wage model's transformed dynamic IS equation, not an
additional assumption.

Let `l` be the labor gap and

\[
q=\sigma(1-\alpha)+\phi+\alpha,\qquad
g_t=q l_t.
\]

The wage-inflation Taylor rule (including Dennery footnote 12's optional
output response) is

\[
i_t=\phi_\pi^w\pi_t^w+\phi_y y_t+\nu_t.
\]

### Worker/union monopoly cartridge

Workers set wages and firms choose employment. Flexible goods prices imply
`W/P=MPL`; in gap form, `mpl_t=-alpha*l_t`. Combining that condition with the
Euler equation gives Dennery equation (8), the intertemporal labor-demand
condition:

\[
[\sigma(1-\alpha)+\alpha](l_t-E_tl_{t+1})
=-(i_t-E_t\pi_{t+1}^w-r_t^n).
\]

Wage Phillips curve:

\[
\pi_t^w=\beta E_t\pi_{t+1}^w+\kappa_w^M l_t,
\]

\[
\kappa_w^M=
\frac{(1-\beta\theta_w)(1-\theta_w)}{\theta_w}
\frac{q}{1+\phi\epsilon_w}>0.
\]

### Employer monopsony cartridge

Firms set wages and households choose employment. The household condition is
`W/P=MRS`, with `mrs_t=sigma*c_t+phi*l_t`. Combining it with the Euler equation
cancels the consumption terms and gives Dennery equation (9), the
intertemporal labor-supply condition:

\[
\phi(l_t-E_tl_{t+1})
=i_t-E_t\pi_{t+1}^w-r_t^n.
\]

Monopsonistic wage Phillips curve (Dennery equation 7 and footnote 13):

\[
\pi_t^w=\beta E_t\pi_{t+1}^w+\kappa_w^m l_t,
\]

\[
\kappa_w^m=-
\frac{(1-\beta\theta_w)(1-\theta_w)}{\theta_w}
\frac{q}{1+\alpha\eta}<0.
\]

Thus `labor_demand_monopoly` and `labor_supply_monopsony` are the two wage-model
counterparts of `dynamic_is`. Each model still has one intertemporal target and
one Phillips-curve target for its two unknowns, `l` and `pi_w`. Adding
`dynamic_is` as a third target would impose the household Euler equation twice
and overdetermine the reduced system. The sign reversal and the
intertemporal-block replacement are both visible in the code and in the
generated DAG difference.

## 4. Five model assemblies

| Model identifier | Equations selected | Unknowns | Zero targets |
|---|---|---|---|
| `rbc` | RBC firm + household + markets | `K`, `L` | goods clearing, Euler equation |
| `rank_calvo_sticky_prices` | Price-rigidity core + Calvo price cartridge | `x`, `pi_p` | dynamic IS, price PC |
| `rank_rotemberg_sticky_prices` | Price-rigidity core + Rotemberg price cartridge | `x`, `pi_p` | dynamic IS, price PC |
| `rank_union_sticky_wages` | Wage core + labor demand + worker/union PC | `l`, `pi_w` | intertemporal demand, wage PC |
| `rank_firm_sticky_wages` | Wage core + labor supply + employer PC | `l`, `pi_w` | intertemporal supply, wage PC |

The numerical authority of these equations is documented separately in
[calibration.md](calibration.md). In particular, the EHL quarterly parameters
are source values, whereas `eta=4` and the wage-inflation policy coefficient are
explicit comparison choices for the monopsony ladder.
