#!/usr/bin/env python3
"""
batplot_v1.0: Interactively plot: 
    XRD data .xye, .xy, .qye, .dat, .csv
    PDF data .gr
    XAS data .nor, .chik, .chir
 More features to be added.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import argparse
import pickle
import random
import sys
from matplotlib.ticker import AutoMinorLocator, NullFormatter
import json
import re

# Set global default font
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'DejaVu Sans', 'Helvetica', 'STIXGeneral', 'Liberation Sans', 'Arial Unicode MS'],
    'mathtext.fontset': 'dejavusans',   # keeps math consistent with Arial-like sans
    'font.size': 16
})


def normalize_label_text(text: str) -> str:
    if not text:
        return text
    # Convert common problematic pattern
    text = text.replace("Å⁻¹", "Å$^{-1}$")
    text = text.replace("Å ^-1", "Å$^{-1}$")
    text = text.replace("Å^-1", "Å$^{-1}$")
    # Also handle plain Angstrom with math formatting if user typed \AA⁻¹
    text = text.replace(r"\AA⁻¹", r"\AA$^{-1}$")
    return text

# ---------------- Overwrite confirmation helper ----------------
def _confirm_overwrite(path: str, auto_suffix: bool = True):
    """Ask user before overwriting an existing file.

    Returns (proceed_path or None). If user declines and auto_suffix is True and
    input is non-interactive (no TTY), generate a non-colliding filename by
    appending _1, _2, ... before extension.
    """
    try:
        if not os.path.exists(path):
            return path
        # If stdin not a tty (e.g. scripted) we avoid blocking; optionally suffix.
        if not sys.stdin.isatty():
            if not auto_suffix:
                return None
            base, ext = os.path.splitext(path)
            k = 1
            new_path = f"{base}_{k}{ext}"
            while os.path.exists(new_path) and k < 1000:
                k += 1
                new_path = f"{base}_{k}{ext}"
            return new_path
        ans = input(f"File '{path}' exists. Overwrite? [y/N]: ").strip().lower()
        if ans == 'y':
            return path
        # Offer alternative name interactively
        alt = input("Enter new filename (blank=cancel): ").strip()
        if not alt:
            return None
        # Ensure extension if user omitted (reuse original ext)
        if not os.path.splitext(alt)[1] and os.path.splitext(path)[1]:
            alt += os.path.splitext(path)[1]
        if os.path.exists(alt):
            print("Chosen alternative also exists; action canceled.")
            return None
        return alt
    except Exception:
        # On any failure, fall back to original path without overwrite protection
        return path

# ---------------- CIF Reading & Pattern Simulation ----------------
def _parse_cif_basic(fname):
    """Parse a CIF file (lightweight)."""
    cell = {'a':None,'b':None,'c':None,'alpha':None,'beta':None,'gamma':None,'space_group':None}
    atoms = []
    sym_ops = []
    atom_headers = []
    in_atom_loop = False
    def _clean_num(tok: str):
        t = tok.strip().strip("'\"")
        t = re.sub(r"\([0-9]+\)$", "", t)
        return t
    with open(fname,'r',encoding='utf-8',errors='ignore') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'): continue
            low = line.lower()
            if low.startswith('_space_group_name_h-m_alt') or low.startswith('_symmetry_space_group_name_h-m'):
                parts=line.split()
                if len(parts)>=2:
                    cell['space_group']=parts[1].strip("'\"")
            if low.startswith('_cell_length_a'):
                try:
                    cell['a']=float(_clean_num(line.split()[1]))
                except Exception:
                    pass
            elif low.startswith('_cell_length_b'):
                try:
                    cell['b']=float(_clean_num(line.split()[1]))
                except Exception:
                    pass
            elif low.startswith('_cell_length_c'):
                try:
                    cell['c']=float(_clean_num(line.split()[1]))
                except Exception:
                    pass
            elif low.startswith('_cell_angle_alpha'):
                try:
                    cell['alpha']=float(_clean_num(line.split()[1]))
                except Exception:
                    pass
            elif low.startswith('_cell_angle_beta'):
                try:
                    cell['beta']=float(_clean_num(line.split()[1]))
                except Exception:
                    pass
            elif low.startswith('_cell_angle_gamma'):
                try:
                    cell['gamma']=float(_clean_num(line.split()[1]))
                except Exception:
                    pass
            if line.lower().startswith('loop_'):
                in_atom_loop=False; atom_headers=[]; continue
            if line.lower().startswith('_space_group_symop_operation_xyz'): continue
            if line.lower().startswith('_atom_site_'):
                atom_headers.append(line)
                if any(h.lower().startswith('_atom_site_fract_x') for h in atom_headers) and \
                   any(h.lower().startswith('_atom_site_fract_y') for h in atom_headers) and \
                   any(h.lower().startswith('_atom_site_fract_z') for h in atom_headers):
                    in_atom_loop=True
                continue
            if (len(atom_headers)==1 and atom_headers[0].lower().startswith('_space_group_symop_operation_xyz') and not line.startswith('_') and ',' in line):
                sym_ops.append(line.strip().strip("'\"")); continue
            if in_atom_loop and not line.startswith('_'):
                toks=line.split();
                if len(toks)<4: continue
                header_map={h.lower():i for i,h in enumerate(atom_headers)}
                def gidx(prefix):
                    for h,i in header_map.items():
                        if h.startswith(prefix): return i
                    return None
                ix=gidx('_atom_site_fract_x'); iy=gidx('_atom_site_fract_y'); iz=gidx('_atom_site_fract_z')
                isym=gidx('_atom_site_type_symbol'); ilab=gidx('_atom_site_label')
                iocc=gidx('_atom_site_occupancy'); iuiso=gidx('_atom_site_u_iso') or gidx('_atom_site_u_iso_or_equiv') or gidx('_atom_site_u_equiv')
                try:
                    x=float(_clean_num(toks[ix])) if ix is not None else 0.0
                    y=float(_clean_num(toks[iy])) if iy is not None else 0.0
                    z=float(_clean_num(toks[iz])) if iz is not None else 0.0
                except: continue
                if isym is not None and isym < len(toks):
                    sym=re.sub(r'[^A-Za-z].*','',toks[isym])
                elif ilab is not None and ilab < len(toks):
                    sym=re.sub(r'[^A-Za-z].*','',toks[ilab])
                else: sym='X'
                if iocc is not None and iocc < len(toks):
                    try:
                        occ=float(_clean_num(toks[iocc]))
                    except Exception:
                        occ=1.0
                else: occ=1.0
                if iuiso is not None and iuiso < len(toks):
                    try:
                        Uiso=float(_clean_num(toks[iuiso]))
                    except Exception:
                        Uiso=None
                else: Uiso=None
                atoms.append((sym,x,y,z,occ,Uiso))
    if any(v is None for v in cell.values()):
        raise ValueError(f"Incomplete cell parameters in CIF {fname}")
    if not atoms: raise ValueError(f"No atoms parsed from CIF {fname}")
    if sym_ops:
        seen=set(); expanded=[]
        if not any(op.replace(' ','') in ('x,y,z','x,y,z,') for op in sym_ops): sym_ops.append('x, y, z')
        def eval_coord(expr,x,y,z):
            expr=expr.strip().lower().replace(' ','')
            if not re.match(r'^[xyz0-9+\-*/().,/]*$',expr): return x
            try: return eval(expr,{"__builtins__":{}},{'x':x,'y':y,'z':z})%1.0
            except: return x
        for sym,x,y,z,occ,Uiso in atoms:
            for op in sym_ops:
                parts=op.strip().strip("'\"").split(',')
                if len(parts)!=3: continue
                nx=eval_coord(parts[0],x,y,z); ny=eval_coord(parts[1],x,y,z); nz=eval_coord(parts[2],x,y,z)
                key=(round(nx,4),round(ny,4),round(nz,4),sym)
                if key in seen: continue
                seen.add(key); expanded.append((sym,nx,ny,nz,occ,Uiso))
        if expanded: atoms=expanded
    return cell, atoms

def _atomic_number_table():
    elements = [
        'H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr','Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn'
    ]
    return {el:i+1 for i,el in enumerate(elements)}

def simulate_cif_pattern_Q(fname, Qmax=10.0, dQ=0.002, peak_width=0.01,
                           wavelength=1.5406, space_group_hint=None):
    """Simulate an (improved) powder diffraction pattern I(Q) from a CIF.

    Changes vs earlier implementation:
      * Full enumeration (±h,±k,±l) so Friedel mates included automatically (multiplicity implicit).
      * Basic centering extinction: P (none), I (h+k+l even), F (all even/odd), C (h+k even), R (hex approx: (-h+k+l)%3==0).
      * Debye–Waller: exp(-B s^2) with s = Q/(4π).
      * Lorentz–polarization (Debye–Scherrer, unpolarized): (1+cos^2 2θ)/(sin^2 θ * sin 2θ).
      * Partial Cromer–Mann set; fallback to damped Z.
    """
    cell, atoms = _parse_cif_basic(fname)
    if space_group_hint is None:
        space_group_hint = cell.get('space_group')

    a, b, c = cell['a'], cell['b'], cell['c']
    alpha = np.deg2rad(cell['alpha'])
    beta = np.deg2rad(cell['beta'])
    gamma = np.deg2rad(cell['gamma'])

    # Lattice vectors
    a_vec = np.array([a, 0, 0], dtype=float)
    b_vec = np.array([b * np.cos(gamma), b * np.sin(gamma), 0], dtype=float)
    c_x = c * np.cos(beta)
    c_y = c * (np.cos(alpha) - np.cos(beta) * np.cos(gamma)) / np.sin(gamma)
    c_z_sq = c ** 2 - c_x ** 2 - c_y ** 2
    c_z = np.sqrt(max(c_z_sq, 1e-12))
    c_vec = np.array([c_x, c_y, c_z], dtype=float)
    A = np.column_stack([a_vec, b_vec, c_vec])
    V = np.dot(a_vec, np.cross(b_vec, c_vec))
    if abs(V) < 1e-10:
        raise ValueError('Invalid cell volume')
    B = 2 * np.pi * np.linalg.inv(A).T
    b1, b2, b3 = B[:, 0], B[:, 1], B[:, 2]
    a_star = np.linalg.norm(b1); b_star = np.linalg.norm(b2); c_star = np.linalg.norm(b3)

    # --- Specialized fast path for cubic bcc single-element (Im-3m) ---
    try:
        cubic_tol = 1e-4
        is_cubic = (abs(a-b) < cubic_tol and abs(a-c) < cubic_tol and
                    abs(cell['alpha']-90) < 1e-3 and abs(cell['beta']-90) < 1e-3 and abs(cell['gamma']-90) < 1e-3)
        # After symmetry expansion atom_data not yet built; infer elements directly from atoms list
        unique_elements = {atm[0].capitalize() for atm in atoms}
        likely_bcc = space_group_hint and space_group_hint.lower().startswith('i') and len(unique_elements) == 1
    except Exception:
        is_cubic = False; likely_bcc = False
    if is_cubic and likely_bcc:
        element = list(unique_elements)[0]
        # Simple multiplicity function for cubic
        def mult_cubic(h,k,l):
            ah, ak, al = abs(h), abs(k), abs(l)
            vals = sorted([ah,ak,al])
            if vals[0]==0 and vals[1]==0 and vals[2]>0:  # h00
                return 6
            if vals[0]==0 and vals[1]>0 and vals[2]>0:
                if vals[1]==vals[2]:  # h h 0
                    return 12
                return 24              # h k 0 (h!=k)
            if vals[0]==vals[1]==vals[2]:  # h h h
                return 8
            if vals[0]==vals[1] or vals[1]==vals[2] or vals[0]==vals[2]:  # h h l (h!=l)
                return 24
            return 48  # h k l all different
        # Enumerate hkl by increasing Q using cubic metric directly
        lam = wavelength if wavelength else 1.5406
        max_index_sq = (Qmax * a / (2*np.pi))**2 + 1
        hkl_intens = []  # (Q, I_raw)
        # Atomic form factor function (reuse partial CM table below after definition). We'll define minimal CM here and then reuse global fallback later.
        CM_LOCAL = {
            'Fe': ([11.7695, 7.3573, 3.5222, 2.3045],[4.7611, 0.3072, 15.3535, 76.8805], 1.0369)
        }
        def fe_form_factor(Q):
            s2 = (Q/(4*np.pi))**2
            if element in CM_LOCAL:
                a_c, b_c, c_c = CM_LOCAL[element]
                f = c_c
                for ai,bi in zip(a_c,b_c):
                    f += ai * np.exp(-bi*s2)
                return max(f,0.0)
            Z = _atomic_number_table().get(element,26)
            return Z * np.exp(-0.002*Q*Q)
        limit = int(np.ceil(np.sqrt(max_index_sq))) + 1
        for h in range(0, limit):
            for k in range(0, limit):
                for l in range(0, limit):
                    if h==k==l==0:
                        continue
                    # bcc extinction: h+k+l even
                    if (h + k + l) % 2 != 0:
                        continue
                    index_sq = h*h + k*k + l*l
                    if index_sq > max_index_sq:
                        continue
                    Q = 2*np.pi*np.sqrt(index_sq)/a
                    if Q <= 0 or Q > Qmax:
                        continue
                    sin_theta = (Q * lam)/(4*np.pi)
                    if sin_theta <= 0 or sin_theta >= 1:
                        continue
                    theta = np.arcsin(sin_theta)
                    f0 = fe_form_factor(Q)
                    F = 2.0 * f0  # bcc: two atoms (0,0,0) & (1/2,1/2,1/2) => 1+(-1)^{h+k+l}=2 for even sum
                    m = mult_cubic(h,k,l)
                    cos_2theta = np.cos(2*theta)
                    # Use conventional combined factor: (1+cos^2 2θ)/(2 sin θ sin 2θ)
                    sin2t = np.sin(2*theta)
                    if sin2t <= 1e-12:
                        continue
                    lp = (1 + cos_2theta*cos_2theta) / (2 * sin_theta * sin2t)
                    I = (F*F) * m * lp
                    hkl_intens.append((Q, I))
        if not hkl_intens:
            raise ValueError('No reflections in range (cubic bcc path)')
        hkl_intens.sort(key=lambda x: x[0])
        Q_ref = np.array([q for q,_ in hkl_intens])
        I_ref = np.array([i for _,i in hkl_intens])
        Q_grid = np.arange(0, Qmax + dQ*0.5, dQ)
        intens = np.zeros_like(Q_grid)
        for q,i in zip(Q_ref, I_ref):
            sigma = peak_width * (0.6 + 0.4*q/Qmax)
            intens += i * np.exp(-0.5*((Q_grid - q)/sigma)**2)
        if intens.max() > 0:
            intens /= intens.max()
        return Q_grid, intens
    hmax = max(1, int(np.ceil(Qmax / a_star)))
    kmax = max(1, int(np.ceil(Qmax / b_star)))
    lmax = max(1, int(np.ceil(Qmax / c_star)))

    Zmap = _atomic_number_table()
    CM_COEFFS = {
        'C':  ([2.3100, 1.0200, 1.5886, 0.8650], [20.8439, 10.2075, 0.5687, 51.6512], 0.2156),
        'N':  ([12.2126, 3.1322, 2.0125, 1.1663], [0.0057, 9.8933, 28.9975, 0.5826], -11.5290),
        'O':  ([3.0485, 2.2868, 1.5463, 0.8670], [13.2771, 5.7011, 0.3239, 32.9089], 0.2508),
        'Si': ([6.2915, 3.0353, 1.9891, 1.5410], [2.4386, 32.3337, 0.6785, 81.6937], 1.1407),
        'Fe': ([11.7695, 7.3573, 3.5222, 2.3045], [4.7611, 0.3072, 15.3535, 76.8805], 1.0369),
        'Ni': ([12.8376, 7.2920, 4.4438, 2.3800], [3.8785, 0.2565, 13.5290, 71.1692], 1.0341),
        'Cu': ([13.3380, 7.1676, 5.6158, 1.6735], [3.5828, 0.2470, 11.3966, 64.8126], 1.1910),
        'Se': ([19.3319, 8.8752, 2.6959, 1.2199], [6.4000, 1.4838, 19.9887, 55.4486], 1.1053),
    }

    def form_factor(sym, Q):
        s2 = (Q / (4 * np.pi)) ** 2
        if sym in CM_COEFFS:
            a, b, c = CM_COEFFS[sym]
            f = c
            for ai, bi in zip(a, b):
                f += ai * np.exp(-bi * s2)
            return max(f, 0.0)
        Z = Zmap.get(sym, 10)
        return Z * np.exp(-0.002 * Q * Q)

    # Atoms with B-factor
    atom_data = []
    for sym, x, y, z, occ, Uiso in atoms:
        sym_cap = sym.capitalize()
        Z = Zmap.get(sym_cap, 10)
        Biso = 8 * np.pi ** 2 * Uiso if Uiso is not None else 0.0
        atom_data.append((sym_cap, x, y, z, occ, Biso))

    def extinct(h, k, l, sg):
        if not sg:
            return False
        sg0 = sg.lower()[0]
        if sg0 == 'p':
            return False
        if sg0 == 'i':
            return (h + k + l) % 2 != 0
        if sg0 == 'f':
            all_even = (h % 2 == 0) and (k % 2 == 0) and (l % 2 == 0)
            all_odd = (h % 2 != 0) and (k % 2 != 0) and (l % 2 != 0)
            return not (all_even or all_odd)
        if sg0 == 'c':
            return (h + k) % 2 != 0
        if sg0 == 'r':
            return ((-h + k + l) % 3) != 0
        return False

    refl_map = {}
    lam = wavelength if wavelength else 1.5406
    for h in range(-hmax, hmax + 1):
        for k in range(-kmax, kmax + 1):
            for l in range(-lmax, lmax + 1):
                if h == 0 and k == 0 and l == 0:
                    continue
                if extinct(h, k, l, space_group_hint):
                    continue
                G = h * b1 + k * b2 + l * b3
                Q = np.linalg.norm(G)
                if Q <= 0 or Q > Qmax:
                    continue
                sin_theta = (Q * lam) / (4 * np.pi)
                if sin_theta <= 0 or sin_theta >= 1:
                    continue
                theta = np.arcsin(sin_theta)
                s2 = (Q / (4 * np.pi)) ** 2
                phases = []
                weights = []
                for sym_cap, ax, ay, az, occ, Biso in atom_data:
                    phase = 2 * np.pi * (h * ax + k * ay + l * az)
                    f0 = form_factor(sym_cap, Q)
                    if f0 <= 1e-8:
                        continue
                    dw = np.exp(-Biso * s2) if Biso > 0 else 1.0
                    w = f0 * occ * dw
                    if w <= 0:
                        continue
                    phases.append(phase)
                    weights.append(w)
                if not weights:
                    continue
                weights = np.array(weights)
                phases = np.array(phases)
                F = np.sum(weights * np.exp(1j * phases))
                I = (F.real ** 2 + F.imag ** 2)
                if I <= 1e-14:
                    continue
                cos_2theta = np.cos(2 * theta)
                sin_theta_sq = np.sin(theta) ** 2
                sin_2theta = np.sin(2 * theta)
                if sin_theta_sq <= 0 or sin_2theta <= 1e-12:
                    continue
                lp = (1 + cos_2theta ** 2) / (sin_theta_sq * sin_2theta)
                qkey = round(Q, 5)
                refl_map[qkey] = refl_map.get(qkey, 0.0) + I * lp

    if not refl_map:
        raise ValueError('No reflections in range')

    refl_items = sorted(refl_map.items())
    refl_Q = np.array([k for k, _ in refl_items])
    refl_I = np.array([v for _, v in refl_items])

    Q_grid = np.arange(0, Qmax + dQ * 0.5, dQ)
    intens = np.zeros_like(Q_grid)
    for q, I in zip(refl_Q, refl_I):
        sigma = peak_width * (0.6 + 0.4 * q / Qmax)
        intens += I * np.exp(-0.5 * ((Q_grid - q) / sigma) ** 2)
    if intens.max() > 0:
        intens /= intens.max()
    return Q_grid, intens

def cif_reflection_positions(fname, Qmax=10.0, wavelength=1.5406, space_group_hint=None):
    """Return sorted list of reflection |Q| positions (Å^-1) up to Qmax (no intensity threshold).

    If wavelength is None: enumerate all reflections up to Qmax (no Bragg cutoff).
    If wavelength provided: apply Bragg condition (sin θ <= 1) to discard unreachable reflections.
    """
    cell, atoms = _parse_cif_basic(fname)
    if space_group_hint is None:
        space_group_hint = cell.get('space_group')
    a,b,c = cell['a'], cell['b'], cell['c']
    alpha = np.deg2rad(cell['alpha']); beta = np.deg2rad(cell['beta']); gamma = np.deg2rad(cell['gamma'])
    a_vec = np.array([a,0,0]); b_vec = np.array([b*np.cos(gamma), b*np.sin(gamma), 0])
    c_x = c*np.cos(beta); c_y = c*(np.cos(alpha)-np.cos(beta)*np.cos(gamma))/np.sin(gamma)
    c_z = np.sqrt(max(c**2 - c_x**2 - c_y**2, 1e-12))
    c_vec = np.array([c_x,c_y,c_z])
    A = np.column_stack([a_vec,b_vec,c_vec])
    V = np.dot(a_vec, np.cross(b_vec, c_vec))
    if abs(V) < 1e-10:
        return []
    B = 2*np.pi * np.linalg.inv(A).T
    b1,b2,b3 = B[:,0],B[:,1],B[:,2]
    a_star,b_star,c_star = np.linalg.norm(b1), np.linalg.norm(b2), np.linalg.norm(b3)
    hmax = max(1,int(np.ceil(Qmax/a_star)))
    kmax = max(1,int(np.ceil(Qmax/b_star)))
    lmax = max(1,int(np.ceil(Qmax/c_star)))
    def extinct(h,k,l,sg):
        if not sg: return False
        c0 = sg.lower()[0]
        if c0=='i': return (h+k+l)%2!=0
        if c0=='f':
            all_even=(h%2==0 and k%2==0 and l%2==0); all_odd=(h%2!=0 and k%2!=0 and l%2!=0)
            return not (all_even or all_odd)
        if c0=='c': return (h+k)%2!=0
        if c0=='r': return ((-h+k+l)%3)!=0
        return False
    lam = wavelength  # may be None for unrestricted Q listing
    refl=set(); hkl_list=[]
    for h in range(-hmax,hmax+1):
        for k in range(-kmax,kmax+1):
            for l in range(-lmax,lmax+1):
                if h==k==l==0: continue
                if extinct(h,k,l,space_group_hint): continue
                G = h*b1 + k*b2 + l*b3
                Q = np.linalg.norm(G)
                if Q<=0 or Q>Qmax: continue
                if lam is not None:
                    s = (Q*lam)/(4*np.pi)
                    if s<=0 or s>=1: continue
                q_round = round(Q,6)
                refl.add(q_round)
                hkl_list.append((q_round,h,k,l))
    refl_sorted = sorted(refl)
    # Store hkl list (may contain duplicates for sym equiv; keep first occurrence per Q & hkl)
    label_map = {}
    if hkl_list:
        seen=set(); compact=[]
        for item in hkl_list:
            if item in seen: continue
            seen.add(item); compact.append(item)
        cif_hkl_map[fname]=compact
        by_q={}
        for q,h,k,l in compact:
            # canonicalize sign
            if h<0 or (h==0 and k<0) or (h==0 and k==0 and l<0):
                h,k,l = -h,-k,-l
            by_q.setdefault(q,set()).add((h,k,l))
        for q,triples in by_q.items():
            ordered = sorted(triples)
            nonneg_all = [t for t in ordered if t[0] >= 0 and t[1] >= 0 and t[2] >= 0]
            use_list = nonneg_all if nonneg_all else ordered
            # Show every positive (canonical) hkl for this Q
            label_map[q] = ", ".join(f"({h} {k} {l})" for h,k,l in use_list)
    else:
        cif_hkl_map[fname]=[]
    cif_hkl_label_map[fname] = label_map
    return refl_sorted

# ---------------- Conversion Function ----------------
def convert_to_qye(filenames, wavelength):
    for fname in filenames:
        if not os.path.isfile(fname):
            print(f"File not found: {fname}")
            continue
        try:
            data = np.loadtxt(fname, comments="#")
        except Exception as e:
            print(f"Error reading {fname}: {e}")
            continue
        if data.ndim == 1:
            data = data.reshape(1, -1)
        if data.shape[1] < 2:
            print(f"Invalid data format in {fname}")
            continue
        x, y = data[:, 0], data[:, 1]
        e = data[:, 2] if data.shape[1] >= 3 else None
        theta_rad = np.radians(x / 2)
        q = 4 * np.pi * np.sin(theta_rad) / wavelength
        out_data = np.column_stack((q, y)) if e is None else np.column_stack((q, y, e))
        base, _ = os.path.splitext(fname)
        out_fname = f"{base}.qye"
        np.savetxt(out_fname, out_data, fmt="% .6f",
                   header=f"# Converted from {fname} using λ={wavelength} Å")
        print(f"Saved {out_fname}")

# ---------------- FullProf row-wise stacking ----------------
def read_fullprof_rowwise(fname):
    with open(fname, "r") as f:
        lines = f.readlines()[1:]
    y_rows = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        y_rows.extend([float(val) for val in line.split()])
    y = np.array(y_rows)
    return y, len(lines)

# ---------------- CSV Reading ----------------
def read_csv_file(fname):
    for delim in [",", ";", "\t"]:
        try:
            data = np.genfromtxt(fname, delimiter=delim, comments="#")
            if data.ndim == 1:
                data = data.reshape(1, -1)
            if data.shape[1] >= 2:
                return data
        except Exception:
            continue
    print(f"Invalid CSV format in {fname}, need at least 2 columns (x,y).")
    return None

# ---------------- .gr (Pair Distribution Function) Reading ----------------
def read_gr_file(fname):
    """
    Read a PDF .gr file (r, G(r)).
    Skips header/comment/non-numeric lines until numeric data (>=2 float cols) start.
    Ignores extra columns beyond first two.
    """
    r_vals = []
    g_vals = []
    # (Removed unused compiled regex float_re)
    with open(fname, "r") as f:
        for line in f:
            ls = line.strip()
            if not ls or ls.startswith("#"):
                continue
            # Quick numeric scan
            parts = ls.replace(",", " ").split()
            # Need at least 2 floats
            floats = []
            for p in parts:
                try:
                    floats.append(float(p))
                except ValueError:
                    break
            if len(floats) >= 2:
                r_vals.append(floats[0])
                g_vals.append(floats[1])
    if not r_vals:
        raise ValueError(f"No numeric data found in {fname}")
    return np.array(r_vals, dtype=float), np.array(g_vals, dtype=float)

# ---------------- label positions ----------------
def update_labels(ax, y_data_list, label_text_objects, stack_mode):
    """
    stack_mode True:
        Each label at (xmax, curve_ymax) in data coordinates.
    stack_mode False:
        Labels form a fixed vertical list at top-right in axes coordinates.
    """
    if not label_text_objects:
        return

    if stack_mode:
        x_max = ax.get_xlim()[1]
        for i, txt in enumerate(label_text_objects):
            if i < len(y_data_list) and len(y_data_list[i]) > 0:
                y_max_curve = float(np.max(y_data_list[i]))
            else:
                y_max_curve = ax.get_ylim()[1]
            txt.set_transform(ax.transData)
            txt.set_position((x_max, y_max_curve))
    else:
        n = len(label_text_objects)
        top_pad = 0.02
        start_y = 1.0 - top_pad
        spacing = min(0.08, max(0.025, 0.90 / max(n, 1)))
        for i, txt in enumerate(label_text_objects):
            y_pos = start_y - i * spacing
            if y_pos < 0.02:
                y_pos = 0.02
            txt.set_transform(ax.transAxes)
            txt.set_position((1.0, y_pos))
    ax.figure.canvas.draw_idle()

# ---------------- Interactive menu ----------------
def interactive_menu(fig, ax, y_data_list, x_data_list, labels, orig_y,
                     label_text_objects, delta, x_label, args,
                     x_full_list, raw_y_full_list, offsets_list,
                     use_Q, use_r, use_E, use_k, use_rft):
    # Ensure globals declared before any assignment in nested handlers
    global show_cif_hkl, cif_extend_suspended
    # REPLACED print_main_menu with column layout (now hides 'd' and 'y' in --stack)
    is_diffraction = use_Q or (not use_r and not use_E and not use_k and not use_rft)  # 2θ or Q
    def print_main_menu():
        has_cif = False
        try:
            has_cif = any(f.lower().endswith('.cif') for f in args.files)
        except Exception:
            pass
        col1 = ["c: colors", "f: font", "l: line", "t: ticks"]
        if has_cif:
            col1.append("z: hkl")
        col2 = ["a: rearrange", "d: offset", "r: rename", "g: size","x: change X", "y: change Y"]
        col3 = ["v: find peaks", "p: print style", "i: import style", "n: crosshair", "e: export", "s: save", "b: undo", "q: quit"]
        if args.stack:
            col2 = [item for item in col2 if not item.startswith("d:") and not item.startswith("y:")]
        if not is_diffraction:
            col3 = [item for item in col3 if not item.startswith("n:")]
        rows = max(len(col1), len(col2), len(col3))
        print("\nInteractive menu:")
        print("  (Styles)         (Geometries)     (Options)")
        for i in range(rows):
            p1 = col1[i] if i < len(col1) else ""
            p2 = col2[i] if i < len(col2) else ""
            p3 = col3[i] if i < len(col3) else ""
            print(f"  {p1:<16} {p2:<16} {p3:<16}")

    # --- Helper for spine visibility ---
    def set_spine_visible(which, visible):
        if which in ax.spines:
            ax.spines[which].set_visible(visible)
            fig.canvas.draw_idle()

    def get_spine_visible(which):
        if which in ax.spines:
            return ax.spines[which].get_visible()
        return False
    # Initial menu display REMOVED to avoid double print
    # print_main_menu()
    ax.set_aspect('auto', adjustable='datalim')

    def on_xlim_change(event_ax):
        update_labels(event_ax, y_data_list, label_text_objects, args.stack)
        # Extend CIF ticks if needed when user pans/zooms horizontally
        try:
            if (not globals().get('cif_extend_suspended', False) and
                hasattr(ax, '_cif_extend_func') and hasattr(ax, '_cif_draw_func') and callable(ax._cif_extend_func)):
                current_xlim = ax.get_xlim()
                xmax = current_xlim[1]
                ax._cif_extend_func(xmax)
        except Exception:
            pass
        fig.canvas.draw()
    ax.callbacks.connect('xlim_changed', on_xlim_change)

    # --------- UPDATED unified font update helper ----------
    def apply_font_changes(new_size=None, new_family=None):
        if new_family:
            # Keep DejaVu Sans as fallback for missing glyphs (superscripts, etc.)
            fallback_chain = ['DejaVu Sans', 'Arial Unicode MS', 'Liberation Sans']
            existing = plt.rcParams.get('font.sans-serif', [])
            new_list = [new_family] + [f for f in fallback_chain if f != new_family] + \
                       [f for f in existing if f not in fallback_chain and f != new_family]
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = new_list
            lf = new_family.lower()
            if any(k in lf for k in ('stix', 'times', 'roman')):
                plt.rcParams['mathtext.fontset'] = 'stix'
            else:
                plt.rcParams['mathtext.fontset'] = 'dejavusans'

        # Set global font size so all future text objects use the new size
        if new_size is not None:
            plt.rcParams['font.size'] = new_size

        # Update curve labels
        for txt in label_text_objects:
            if new_size is not None:
                txt.set_fontsize(new_size)
            if new_family:
                txt.set_fontfamily(new_family)

        # Axis labels (re-normalize in case glyphs missing)
        for axis_label in (ax.xaxis.label, ax.yaxis.label):
            cur = axis_label.get_text()
            norm = normalize_label_text(cur)
            if norm != cur:
                axis_label.set_text(norm)
            if new_size is not None:
                axis_label.set_fontsize(new_size)
            if new_family:
                axis_label.set_fontfamily(new_family)

        # Top duplicate label
        if hasattr(ax, '_top_xlabel_artist') and ax._top_xlabel_artist is not None:
            if new_size is not None:
                ax._top_xlabel_artist.set_fontsize(new_size)
            if new_family:
                ax._top_xlabel_artist.set_fontfamily(new_family)

        # Right duplicate manual label
        if hasattr(ax, '_right_ylabel_artist') and ax._right_ylabel_artist is not None:
            if new_size is not None:
                ax._right_ylabel_artist.set_fontsize(new_size)
            if new_family:
                ax._right_ylabel_artist.set_fontfamily(new_family)

        # Tick labels
        for lbl in ax.get_xticklabels() + ax.get_yticklabels():
            if new_size is not None:
                lbl.set_fontsize(new_size)
            if new_family:
                lbl.set_fontfamily(new_family)

        fig.canvas.draw_idle()

    # Generic font sync (even when size/family unchanged) so newly created labels/twin axes inherit the rcParams size
    def sync_fonts():
        try:
            base_size = plt.rcParams.get('font.size')
            if base_size is None:
                return
            # Curve labels
            for txt in label_text_objects:
                txt.set_fontsize(base_size)
            # Axis labels
            if ax.xaxis.label: ax.xaxis.label.set_fontsize(base_size)
            if ax.yaxis.label: ax.yaxis.label.set_fontsize(base_size)
            # Top duplicate label
            if hasattr(ax, '_top_xlabel_artist') and ax._top_xlabel_artist is not None:
                ax._top_xlabel_artist.set_fontsize(base_size)
            # Right duplicate manual label
            if hasattr(ax, '_right_ylabel_artist') and ax._right_ylabel_artist is not None:
                ax._right_ylabel_artist.set_fontsize(base_size)
            # Tick labels main axes
            for tl in ax.get_xticklabels() + ax.get_yticklabels():
                tl.set_fontsize(base_size)
            fig.canvas.draw_idle()
        except Exception:
            pass

    # Adjust vertical position of duplicate top X label depending on top tick visibility
    def position_top_xlabel():
        try:
            if not getattr(ax, '_top_xlabel_on', False):
                return
            if not hasattr(ax, '_top_xlabel_artist') or ax._top_xlabel_artist is None:
                return
            # Base offset above axes top; increase if top ticks & labels visible
            if tick_state.get('tx', False):
                # More space for tick labels (rough heuristic)
                y_off = 0.09
            else:
                y_off = 0.02
            ax._top_xlabel_artist.set_position((0.5, 1.0 + y_off))
            fig.canvas.draw_idle()
        except Exception:
            pass

    def position_right_ylabel():
        """Adjust manual duplicate right Y label horizontal offset depending on right tick visibility."""
        try:
            if not getattr(ax, '_right_ylabel_on', False):
                return
            art = getattr(ax, '_right_ylabel_artist', None)
            if art is None:
                return
            if tick_state.get('ry', False):
                x_off = 1.10
            else:
                x_off = 1.02
            art.set_position((x_off, 0.5))
            fig.canvas.draw_idle()
        except Exception:
            pass
    def play_jump_game():
        """
        Simple terminal 'jumping bird' (Flappy-style) game.
        Controls: j = jump, Enter = let bird fall, q = quit game.
        Avoid hitting '#' pillars. Gap moves left each tick.
        Score = pillars passed.
        """
        WIDTH = 32
        HEIGHT =  nine = 9  # make height obvious
        HEIGHT = 9
        BIRD_X = 5
        GRAVITY = 1
        JUMP_VEL = -2
        GAP_SIZE = 3
        MIN_OBS_SPACING = 6

        class Obstacle:
            __slots__ = ("x", "gap_start", "scored")
            def __init__(self, x):
                self.x = x
                self.gap_start = random.randint(1, HEIGHT - GAP_SIZE - 1)
                self.scored = False

        bird_y = HEIGHT // 2
        vel = 0
        tick = 0
        score = 0
        obstacles = [Obstacle(WIDTH - 1)]

        def need_new():
            if not obstacles:
                return True
            rightmost = max(o.x for o in obstacles)
            return rightmost < WIDTH - MIN_OBS_SPACING

        def new_obstacle():
            obstacles.append(Obstacle(WIDTH - 1))

        def move_obstacles():
            for o in obstacles:
                o.x -= 1

        def purge_obstacles():
            while obstacles and obstacles[0].x < -1:
                obstacles.pop(0)

        def render():
            top_border = "+" + "-" * WIDTH + "+"
            print("\n" + top_border)
            for y in range(HEIGHT):
                row_chars = []
                for x in range(WIDTH):
                    ch = " "
                    # bird
                    if x == BIRD_X and y == bird_y:
                        ch = "@"
                    # obstacle
        print("  q         -> quit game")
        print("Bird = @  | Score increments when you pass a pillar.\n")

        while True:
            render()
            cmd = input("> ").strip().lower()
            if cmd == 'q':
                print("Exited game. Returning to interactive menu.\n")
                break
            if cmd == 'j':
                vel = JUMP_VEL  # jump impulse
            else:
                vel += GRAVITY  # falling acceleration

            bird_y += vel
            # Soft clamp: if hits boundary, treat as collision next loop render
            move_obstacles()
            if need_new():
                new_obstacle()
            purge_obstacles()

            # Scoring: pillar passed when it moves left of bird
            for o in obstacles:
                if not o.scored and o.x < BIRD_X:
                    o.scored = True
                    score += 1

            tick += 1
            if collision():
                render()
                print(f"Game Over! Final score: {score}\n")
                break

    # -------------------------------------------------------

    # --------- NEW: Resize only the plotting frame (axes), keep canvas (figure) size fixed ----------
    def resize_plot_frame():
        """Interactively resize ONLY the data plotting area (axes) in inches.

        Previous version changed the physical figure (window) size. Now we treat
        the numbers the user enters as the desired width/height of the axes
        region inside the existing, fixed-size figure canvas. Margins are
        recomputed to center that axes region. If a single number is given the
        aspect of the current axes is preserved. 'scale=' scales current axes
        size (not the figure).
        """
        try:
            fig_w_in, fig_h_in = fig.get_size_inches()
            # Current axes bbox (figure fraction)
            ax_bbox = ax.get_position()
            cur_ax_w_in = ax_bbox.width * fig_w_in
            cur_ax_h_in = ax_bbox.height * fig_h_in
            print(f"Current canvas (fixed): {fig_w_in:.2f} x {fig_h_in:.2f} in")
            print(f"Current plot frame:     {cur_ax_w_in:.2f} x {cur_ax_h_in:.2f} in (W x H)")
            spec = input("Enter new plot frame size (e.g. '6 4', '6x4', 'w=6 h=4', 'scale=1.2', single width, q=cancel): ").strip().lower()
            if not spec or spec == 'q':
                print("Canceled.")
                return

            # Parse desired axes size
            new_w_in, new_h_in = cur_ax_w_in, cur_ax_h_in
            if 'scale=' in spec:
                try:
                    factor = float(spec.split('scale=')[1].strip())
                    new_w_in = cur_ax_w_in * factor
                    new_h_in = cur_ax_h_in * factor
                except Exception:
                    print("Invalid scale factor.")
                    return
            else:
                parts = spec.replace('x', ' ').split()
                kv = {}
                numbers = []
                for p in parts:
                    if '=' in p:
                        k, v = p.split('=', 1)
                        kv[k.strip()] = v.strip()
                    else:
                        numbers.append(p)
                if kv:
                    if 'w' in kv: new_w_in = float(kv['w'])
                    if 'h' in kv: new_h_in = float(kv['h'])
                elif len(numbers) == 2:
                    new_w_in, new_h_in = float(numbers[0]), float(numbers[1])
                elif len(numbers) == 1:
                    new_w_in = float(numbers[0])
                    aspect = cur_ax_h_in / cur_ax_w_in if cur_ax_w_in else 1.0
                    new_h_in = new_w_in * aspect
                else:
                    print("Could not parse specification.")
                    return

            # Preserve the originally requested values for messaging
            req_w_in, req_h_in = new_w_in, new_h_in
            # Clamp against figure size & minimum margins
            min_margin_frac = 0.05  # 5% each side minimum
            max_w_in = fig_w_in * (1 - 2 * min_margin_frac)
            max_h_in = fig_h_in * (1 - 2 * min_margin_frac)
            if new_w_in > max_w_in:
                print(f"Requested width {new_w_in:.2f} exceeds max {max_w_in:.2f}; clamped.")
                new_w_in = max_w_in
            if new_h_in > max_h_in:
                print(f"Requested height {new_h_in:.2f} exceeds max {max_h_in:.2f}; clamped.")
                new_h_in = max_h_in
            min_ax_in = 0.25  # don't let it vanish
            new_w_in = max(min_ax_in, new_w_in)
            new_h_in = max(min_ax_in, new_h_in)

            # If user entered numbers equal (within tol) to the FIGURE size, interpret as
            # "maximise plot frame" but do NOT treat later printouts as figure resize.
            tol = 1e-3
            requesting_full_canvas = (abs(req_w_in - fig_w_in) < tol and abs(req_h_in - fig_h_in) < tol)

            # Desired fractions of figure
            w_frac = new_w_in / fig_w_in
            h_frac = new_h_in / fig_h_in
            same_axes = False
            if hasattr(fig, '_last_user_axes_inches'):
                pw, ph = fig._last_user_axes_inches
                if abs(pw - new_w_in) < tol and abs(ph - new_h_in) < tol:
                    same_axes = True

            if same_axes and hasattr(fig, '_last_user_margins'):
                # Idempotent: restore previous margins & quick visibility check
                lm, bm, rm, tm = fig._last_user_margins
                fig.subplots_adjust(left=lm, bottom=bm, right=rm, top=tm)
                update_labels(ax, y_data_list, label_text_objects, args.stack)
                if not ensure_text_visibility(check_only=True):
                    fig.canvas.draw_idle()
                    print(f"Plot frame unchanged ({new_w_in:.2f} x {new_h_in:.2f} in); layout preserved.")
                    return
                # Overflow happened meanwhile -> fall through to adjust

            # Center the axes region with requested size
            left = (1 - w_frac) / 2
            right = left + w_frac
            bottom = (1 - h_frac) / 2
            top = bottom + h_frac

            # Safety clamps
            left = max(min_margin_frac, left)
            bottom = max(min_margin_frac, bottom)
            right = min(1 - min_margin_frac, right)
            top = min(1 - min_margin_frac, top)
            # Ensure ordering
            if right - left < 0.05 or top - bottom < 0.05:
                print("Requested frame too small after safety clamps; aborting.")
            else:
                fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)

            update_labels(ax, y_data_list, label_text_objects, args.stack)
            ensure_text_visibility()

            sp = fig.subplotpars
            fig._last_user_axes_inches = ( (sp.right - sp.left) * fig_w_in,
                                           (sp.top   - sp.bottom) * fig_h_in )
            fig._last_user_margins = (sp.left, sp.bottom, sp.right, sp.top)

            # Report final frame size
            final_w_in = (sp.right - sp.left) * fig_w_in
            final_h_in = (sp.top - sp.bottom) * fig_h_in
            if requesting_full_canvas:
                print(f"Requested full-canvas frame. Canvas remains {fig_w_in:.2f} x {fig_h_in:.2f} in; frame now {final_w_in:.2f} x {final_h_in:.2f} in (maximum with minimum margins {min_margin_frac*100:.0f}%).")
            else:
                print(f"Plot frame set to {final_w_in:.2f} x {final_h_in:.2f} in inside fixed canvas {fig_w_in:.2f} x {fig_h_in:.2f} in.")
        except Exception as e:
            print(f"Error resizing plot frame: {e}")

    def resize_canvas():
        """Resize the actual figure (canvas) size in inches while preserving the physical
        plot frame (axes) size in inches as much as possible. If the new canvas is
        too small to hold the previous frame with minimum margins, the frame is
        proportionally reduced but never enlarged implicitly.
        """
        try:
            cur_w, cur_h = fig.get_size_inches()
            bbox_before = ax.get_position()
            frame_w_in_before = bbox_before.width * cur_w
            frame_h_in_before = bbox_before.height * cur_h
            print(f"Current canvas size: {cur_w:.2f} x {cur_h:.2f} in (frame {frame_w_in_before:.2f} x {frame_h_in_before:.2f} in)")
            spec = input("Enter new canvas size (e.g. '8 6', '6x4', 'w=6 h=5', 'scale=1.2', q=cancel): ").strip().lower()
            if not spec or spec == 'q':
                print("Canceled.")
                return
            new_w, new_h = cur_w, cur_h
            if 'scale=' in spec:
                try:
                    fct = float(spec.split('scale=')[1])
                    new_w, new_h = cur_w * fct, cur_h * fct
                except Exception:
                    print("Invalid scale factor.")
                    return
            else:
                parts = spec.replace('x',' ').split()
                kv = {}; nums = []
                for p in parts:
                    if '=' in p:
                        k,v = p.split('=',1); kv[k.strip()] = v.strip()
                    else:
                        nums.append(p)
                if kv:
                    if 'w' in kv: new_w = float(kv['w'])
                    if 'h' in kv: new_h = float(kv['h'])
                elif len(nums)==2:
                    new_w, new_h = float(nums[0]), float(nums[1])
                elif len(nums)==1:
                    new_w = float(nums[0]); aspect = cur_h/cur_w if cur_w else 1.0; new_h = new_w * aspect
                else:
                    print("Could not parse specification.")
                    return
            min_size = 1.0
            new_w = max(min_size, new_w)
            new_h = max(min_size, new_h)
            tol = 1e-3
            same = hasattr(fig,'_last_canvas_size') and all(abs(a-b)<tol for a,b in zip(fig._last_canvas_size,(new_w,new_h)))
            # Set new canvas size first
            fig.set_size_inches(new_w, new_h, forward=True)
            # Attempt to preserve previous absolute frame size
            bbox_after = ax.get_position()  # still old fractions
            # Desired fractions to maintain absolute size: fw_frac = frame_w_in_before / new_w, etc.
            desired_w_frac = frame_w_in_before / new_w
            desired_h_frac = frame_h_in_before / new_h
            # Minimum margin fraction
            min_margin = 0.05
            # If desired fractions exceed space ( > 1 - 2*min_margin), clamp
            max_w_frac = 1 - 2*min_margin
            max_h_frac = 1 - 2*min_margin
            if desired_w_frac > max_w_frac:
                desired_w_frac = max_w_frac
            if desired_h_frac > max_h_frac:
                desired_h_frac = max_h_frac
            # Center the frame using desired fractions
            left = (1 - desired_w_frac) / 2
            bottom = (1 - desired_h_frac) / 2
            right = left + desired_w_frac
            top = bottom + desired_h_frac
            # Safety ordering
            if right - left > 0.05 and top - bottom > 0.05:
                fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
            fig._last_canvas_size = (new_w, new_h)
            # Report final frame size
            bbox_final = ax.get_position()
            final_frame_w_in = bbox_final.width * new_w
            final_frame_h_in = bbox_final.height * new_h
            if same:
                print(f"Canvas unchanged ({new_w:.2f} x {new_h:.2f} in). Frame {final_frame_w_in:.2f} x {final_frame_h_in:.2f} in.")
            else:
                # Indicate if clamped
                note = ""
                if abs(final_frame_w_in - frame_w_in_before) > 1e-3 or abs(final_frame_h_in - frame_h_in_before) > 1e-3:
                    note = " (clamped to fit)" if final_frame_w_in < frame_w_in_before or final_frame_h_in < frame_h_in_before else ""
                print(f"Canvas resized to {new_w:.2f} x {new_h:.2f} in; frame preserved at {final_frame_w_in:.2f} x {final_frame_h_in:.2f} in{note} (was {frame_w_in_before:.2f} x {frame_h_in_before:.2f}).")
            fig.canvas.draw_idle()
        except Exception as e:
            print(f"Error resizing canvas: {e}")
    # -------------------------------------------------

    # ---- Tick / label visibility state ----
    tick_state = {
        'bx': True,
        'tx': False,
        'ly': True,
        'ry': False,
        'mbx': False,
        'mtx': False,
        'mly': False,
        'mry': False
    }

    # NEW: dynamic margin adjustment for top/right ticks
    # Flag to preserve a manual/initial interactive top margin override
    if not hasattr(fig, '_interactive_top_locked'):
        fig._interactive_top_locked = False

    def adjust_margins():
        """Lightweight margin tweak based on tick visibility.

        Unlike the old version this DOES NOT try to aggressively reallocate
        space or change apparent plot size; it only adds a small padding on
        sides that show ticks so labels have breathing room. Intended to be
        idempotent and minimally invasive. Called during initial setup & some
        style operations, but not on every tick toggle anymore.
        """
        sp = fig.subplotpars
        # Start from current to avoid jumping
        left, right, bottom, top = sp.left, sp.right, sp.bottom, sp.top
        pad = 0.01  # modest expansion per active side
        max_pad = 0.10
        # Expand outward (shrinks axes) only if room
        if tick_state['ly'] and left < 0.25:
            left = min(left + pad, 0.40)
        if tick_state['ry'] and (1 - right) < 0.25:
            right = max(right - pad, 0.60)
        if tick_state['bx'] and bottom < 0.25:
            bottom = min(bottom + pad, 0.40)
        if tick_state['tx'] and (1 - top) < 0.25:
            top = max(top - pad, 0.60)

        # Keep minimum plot span
        if right - left < 0.25:
            # Undo horizontal change proportionally
            mid = (left + right) / 2
            left = mid - 0.125
            right = mid + 0.125
        if top - bottom < 0.25:
            mid = (bottom + top) / 2
            bottom = mid - 0.125
            top = mid + 0.125

        fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)

    def ensure_text_visibility(max_iterations=4, check_only=False):
        """Keep all axis & curve labels inside the fixed canvas by nudging margins.

        ONLY adjusts subplot params (left/right/top/bottom); never changes the
        physical figure size. Returns True if any overflow existed (or would
        require adjustment), False otherwise when check_only=True.
        """
        try:
            renderer = fig.canvas.get_renderer()
        except Exception:
            fig.canvas.draw()
            try:
                renderer = fig.canvas.get_renderer()
            except Exception:
                return
        if renderer is None:
            return

        def collect(renderer_obj):
            items = []
            if ax.xaxis.label.get_text():
                try: items.append(ax.xaxis.label.get_window_extent(renderer=renderer_obj))
                except Exception: pass
            if ax.yaxis.label.get_text():
                try: items.append(ax.yaxis.label.get_window_extent(renderer=renderer_obj))
                except Exception: pass
            for t in label_text_objects:
                try: items.append(t.get_window_extent(renderer=renderer_obj))
                except Exception: pass
            return items

        fig_w, fig_h = fig.get_size_inches(); dpi = fig.dpi
        W, H = fig_w * dpi, fig_h * dpi
        pad = 2
        def is_out(bb):
            return (bb.x0 < -pad or bb.y0 < -pad or bb.x1 > W + pad or bb.y1 > H + pad)

        initial = collect(renderer)
        overflow = any(is_out(bb) for bb in initial)
        if check_only:
            return overflow
        if not overflow:
            return False

        for _ in range(max_iterations):
            sp = fig.subplotpars
            left, right, bottom, top = sp.left, sp.right, sp.bottom, sp.top
            changed = False
            for bb in collect(renderer):
                if not is_out(bb):
                    continue
                # Each adjustment shrinks the axes slightly in the offending direction
                if bb.x0 < 0 and left < 0.40:
                    left = min(left + 0.01, 0.40); changed = True
                if bb.x1 > W and right > left + 0.25:
                    right = max(right - 0.01, left + 0.25); changed = True
                if bb.y0 < 0 and bottom < 0.40:
                    bottom = min(bottom + 0.01, 0.40); changed = True
                if bb.y1 > H and top > bottom + 0.25:
                    top = max(top - 0.01, bottom + 0.25); changed = True
            if not changed:
                break
            fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
            fig.canvas.draw()
            try:
                renderer = fig.canvas.get_renderer()
            except Exception:
                break
            # If everything now inside, stop early
            if not any(is_out(bb) for bb in collect(renderer)):
                break
        return True

    def update_tick_visibility():
        ax.tick_params(axis='x',
                       bottom=tick_state['bx'], labelbottom=tick_state['bx'],
                       top=tick_state['tx'],    labeltop=tick_state['tx'])
        ax.tick_params(axis='y',
                       left=tick_state['ly'],  labelleft=tick_state['ly'],
                       right=tick_state['ry'], labelright=tick_state['ry'])

        if tick_state['mbx'] or tick_state['mtx']:
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.tick_params(axis='x', which='minor',
                           bottom=tick_state['mbx'],
                           top=tick_state['mtx'],
                           labelbottom=False, labeltop=False)
        else:
            ax.tick_params(axis='x', which='minor',
                           bottom=False, top=False,
                           labelbottom=False, labeltop=False)

        if tick_state['mly'] or tick_state['mry']:
            ax.yaxis.set_minor_locator(AutoMinorLocator())
            ax.yaxis.set_minor_formatter(NullFormatter())
            ax.tick_params(axis='y', which='minor',
                           left=tick_state['mly'],
                           right=tick_state['mry'],
                           labelleft=False, labelright=False)
        else:
            ax.tick_params(axis='y', which='minor',
                           left=False, right=False,
                           labelleft=False, labelright=False)

    # NOTE: Previously we auto-adjusted subplot margins here based on which
    # sides had ticks visible (calling adjust_margins()). This caused the
    # plotted data area to resize every time the user toggled bx/tx/ly/ry
    # (or minor variants) in the 'h' menu. Per user request, we disable
    # that behavior so changing tick visibility does NOT change the plot
    # size or axes extent. If manual margin adjustments are desired, they
    # can still be triggered via figure resize (menu 'g') or style import.
    # If needed in future, re-enable by uncommenting the next line.
    # adjust_margins()
    ensure_text_visibility()
    fig.canvas.draw_idle()

    # NEW helper (was referenced in 'h' menu but not defined previously)
    def print_tick_state():
        print("Tick visibility state:")
        for k in sorted(tick_state.keys()):
            print(f"  {k:<3} : {'ON ' if tick_state[k] else 'off'}")

    # NEW: style / diagnostics printer (clean version)
    def print_style_info():
        print("\n--- Style / Diagnostics ---")
        fw, fh = fig.get_size_inches()
        print(f"Figure size (inches): {fw:.3f} x {fh:.3f}")
        print(f"Figure DPI: {fig.dpi}")
        bbox = ax.get_position()
        print(f"Axes position (figure fraction): x0={bbox.x0:.3f}, y0={bbox.y0:.3f}, w={bbox.width:.3f}, h={bbox.height:.3f}")
        frame_w_in = bbox.width * fw
        frame_h_in = bbox.height * fh
        print(f"Plot frame size (inches):  {frame_w_in:.3f} x {frame_h_in:.3f}")
        sp = fig.subplotpars
        print(f"Margins (subplot fractions): left={sp.left:.3f}, right={sp.right:.3f}, "
              f"bottom={sp.bottom:.3f}, top={sp.top:.3f}")
        # Axes ranges
        xlim = ax.get_xlim(); ylim = ax.get_ylim()
        print(f"X range: {xlim[0]:.6g} .. {xlim[1]:.6g}")
        print(f"Y range: {ylim[0]:.6g} .. {ylim[1]:.6g}")
        # Axis labels
        print(f"X label: {ax.get_xlabel()}")
        print(f"Y label: {ax.get_ylabel()}")
        # Font info
        if label_text_objects:
            fs_any = label_text_objects[0].get_fontsize(); ff_any = label_text_objects[0].get_fontfamily()
        else:
            fs_any = plt.rcParams.get('font.size'); ff_any = plt.rcParams.get('font.family')
        print(f"Effective font size (labels/ticks): {fs_any}")
        print(f"Font family chain (rcParams['font.sans-serif']): {plt.rcParams.get('font.sans-serif')}")
        print(f"Mathtext fontset: {plt.rcParams.get('mathtext.fontset')}")
        # Tick state
        print_tick_state()
        # Tick widths helper
        def axis_tick_width(axis, which):
            ticks = axis.get_major_ticks() if which == 'major' else axis.get_minor_ticks()
            for t in ticks:
                line = t.tick1line
                if line.get_visible():
                    return line.get_linewidth()
            return None
        x_major_w = axis_tick_width(ax.xaxis, 'major')
        x_minor_w = axis_tick_width(ax.xaxis, 'minor')
        y_major_w = axis_tick_width(ax.yaxis, 'major')
        y_minor_w = axis_tick_width(ax.yaxis, 'minor')
        print(f"Tick widths (major/minor): X=({x_major_w}, {x_minor_w})  Y=({y_major_w}, {y_minor_w})")
        # Spines
        print("Spines:")
        for name, spn in ax.spines.items():
            print(f"  {name:<5} lw={spn.get_linewidth()} color={spn.get_edgecolor()} visible={spn.get_visible()}")
        # Global flags
        print(f"Mode: stack={'yes' if args.stack else 'no'}, autoscale={'yes' if args.autoscale else 'no'}, raw={'yes' if args.raw else 'no'}")
        print(f"Current delta (offset spacing): {delta} (initial args.delta={args.delta})")
        # Curves
        print("Curves:")
        for i, ln in enumerate(ax.lines):
            col = ln.get_color(); lw = ln.get_linewidth(); ls = ln.get_linestyle()
            mk = ln.get_marker(); a = ln.get_alpha()
            xd, yd = ln.get_xdata(orig=False), ln.get_ydata(orig=False)
            npts = len(xd)
            xmn = np.min(xd) if npts else None; xmx = np.max(xd) if npts else None
            ymn = np.min(yd) if npts else None; ymx = np.max(yd) if npts else None
            off = offsets_list[i] if i < len(offsets_list) else None
            base_label = labels[i] if i < len(labels) else ""
            print(f"  {i+1:02d}: label='{base_label}' n={npts} color={col} lw={lw} ls={ls} marker={mk} alpha={a} "
                  f"x=[{xmn},{xmx}] y=[{ymn},{ymx}] offset={off}")
        print(f"Number of curves: {len(ax.lines)}")
        print(f"Stored full-length arrays: {len(x_full_list)} (x_full_list), {len(raw_y_full_list)} (raw_y_full_list)")
        print(f"Normalization: {'raw intensities' if args.raw else 'per-curve max scaled to 1 (current window)'}")
        # Axis title placement state
        try:
            print(f"Axis titles: bottom_x={'ON' if ax.get_xlabel() else 'off'} top_x={'ON' if getattr(ax,'_top_xlabel_on', False) else 'off'} "
                  f"left_y={'ON' if ax.get_ylabel() else 'off'} right_y={'ON' if getattr(ax,'_right_ylabel_on', False) else 'off'}")
        except Exception:
            pass
        print("--- End diagnostics ---\n")

    # NEW: export current style to .bpcfg
    def export_style_config(filename):
        try:
            fw, fh = fig.get_size_inches()
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            sp = fig.subplotpars

            def axis_tick_width(axis, which):
                ticks = axis.get_major_ticks() if which == 'major' else axis.get_minor_ticks()
                for t in ticks:
                    line = t.tick1line
                    if line.get_visible():
                        return line.get_linewidth()
                return None
            # Save spine visibility
            spine_vis = {name: sp.get_visible() for name, sp in ax.spines.items()}

            bbox = ax.get_position()
            frame_w_in = bbox.width * fw
            frame_h_in = bbox.height * fh
            cfg = {
                "figure": {
                    "size": [fw, fh],            # canvas size
                    "dpi": fig.dpi,
                    "frame_size": [frame_w_in, frame_h_in],  # axes (plot frame) size
                    "axes_fraction": [bbox.x0, bbox.y0, bbox.width, bbox.height]
                },
                "axes": {
                    "xlabel": ax.get_xlabel(),
                    "ylabel": ax.get_ylabel(),
                    "xlim": list(xlim),
                    "ylim": list(ylim)
                },
                "margins": {
                    "left":  sp.left,
                    "right": sp.right,
                    "bottom": sp.bottom,
                    "top":   sp.top
                },
                "font": {
                    "size": plt.rcParams.get('font.size'),
                    "family_chain": plt.rcParams.get('font.sans-serif')
                },
                "ticks": {
                    "visibility": tick_state.copy(),
                    "x_major_width": axis_tick_width(ax.xaxis, 'major'),
                    "x_minor_width": axis_tick_width(ax.xaxis, 'minor'),
                    "y_major_width": axis_tick_width(ax.yaxis, 'major'),
                    "y_minor_width": axis_tick_width(ax.yaxis, 'minor')
                },
                "spines": {
                    name: {
                        "linewidth": sp.get_linewidth(),
                        "color": sp.get_edgecolor(),
                        "visible": spine_vis.get(name, True)
                    } for name, sp in ax.spines.items()
                },
                "lines": [
                    {
                        "index": i,
                        "label": (labels[i] if i < len(labels) else ""),
                        "color": ln.get_color(),
                        "linewidth": ln.get_linewidth(),
                        "linestyle": ln.get_linestyle(),
                        "marker": ln.get_marker(),
                        "markersize": ln.get_markersize(),
                        "markerfacecolor": ln.get_markerfacecolor(),
                        "markeredgecolor": ln.get_markeredgecolor(),
                        "alpha": ln.get_alpha()
                    } for i, ln in enumerate(ax.lines)
                ],
                "delta": delta,
                "mode": {
                    "stack": bool(args.stack),
                    "autoscale": bool(args.autoscale),
                    "raw": bool(args.raw)
                },
                "layout": {
                    "label_layout": "stack" if args.stack else "block_top_right",
                    "xaxis_type": ("Q" if use_Q else
                                   ("r" if use_r else
                                    ("E" if use_E else
                                     ("k" if use_k else
                                      ("rft" if use_rft else "2theta")))))
                },
                "normalization": "raw" if args.raw else "normalized"
            }
            # Axis title toggle state
            cfg["axis_titles"] = {
                "top_x": bool(getattr(ax, '_top_xlabel_on', False)),
                "right_y": bool(getattr(ax, '_right_ylabel_on', False)),
                "has_bottom_x": bool(ax.get_xlabel()),
                "has_left_y": bool(ax.get_ylabel())
            }
            # Export CIF tick sets (labels & colors) if present
            if cif_tick_series:
                cfg["cif_ticks"] = [
                    {
                        "index": i,
                        "label": lab,
                        "color": color
                    } for i,(lab,fname,peaksQ,wl,qmax_sim,color) in enumerate(cif_tick_series)
                ]
            if not filename.endswith(".bpcfg"):
                filename += ".bpcfg"
            target = _confirm_overwrite(filename)
            if not target:
                print("Style export canceled.")
                return
            with open(target, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
            print(f"Exported style to {target}")
        except Exception as e:
            print(f"Error exporting style: {e}")

    # NEW: apply imported style config (restricted application)
    def apply_style_config(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception as e:
            print(f"Could not read config: {e}")
            return
        try:
            figure_cfg = cfg.get("figure", {})
            sz = figure_cfg.get("size")
            if isinstance(sz, (list, tuple)) and len(sz) == 2:
                try:
                    fw = float(sz[0]); fh = float(sz[1])
                    if not globals().get('keep_canvas_fixed', True):
                        fig.set_size_inches(fw, fh, forward=True)
                    else:
                        print("(Canvas fixed) Ignoring style figure size request.")
                except Exception as e:
                    print(f"Warning: could not parse figure size: {e}")
            # Optional frame restoration (axes bbox) if provided
            try:
                frame_size = figure_cfg.get('frame_size')
                axes_frac = figure_cfg.get('axes_fraction')
                if axes_frac and isinstance(axes_frac,(list,tuple)) and len(axes_frac)==4:
                    x0,y0,w,h = axes_frac
                    left = float(x0); bottom = float(y0); right = left + float(w); top = bottom + float(h)
                    if 0 < left < right <=1 and 0 < bottom < top <=1:
                        fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
                elif frame_size and isinstance(frame_size,(list,tuple)) and len(frame_size)==2:
                    # Reconstruct approximate fractions to target absolute frame size inside current canvas
                    cur_fw, cur_fh = fig.get_size_inches()
                    des_w, des_h = float(frame_size[0]), float(frame_size[1])
                    min_margin = 0.05
                    w_frac = min(des_w/cur_fw, 1-2*min_margin)
                    h_frac = min(des_h/cur_fh, 1-2*min_margin)
                    left = (1 - w_frac)/2; bottom = (1 - h_frac)/2
                    fig.subplots_adjust(left=left, right=left+w_frac, bottom=bottom, top=bottom+h_frac)
            except Exception:
                pass
            if "dpi" in figure_cfg:
                try:
                    fig.set_dpi(int(figure_cfg["dpi"]))
                except Exception:
                    pass
            # <<< END NEW BLOCK

            # ---- Font ----
            font_cfg = cfg.get("font", {})
            fam_chain = font_cfg.get("family_chain")
            size_val = font_cfg.get("size")
            if fam_chain:
                plt.rcParams['font.family'] = 'sans-serif'
                plt.rcParams['font.sans-serif'] = fam_chain
            numeric_size = None
            if size_val is not None:
                try:
                    numeric_size = float(size_val)
                except Exception:
                    numeric_size = None

            # ---- Axes labels ----
            axes_cfg = cfg.get("axes", {})
            if "xlabel" in axes_cfg:
                ax.set_xlabel(axes_cfg["xlabel"])
            if "ylabel" in axes_cfg:
                ax.set_ylabel(axes_cfg["ylabel"])

            # Apply font changes to existing text objects
            if fam_chain or numeric_size is not None:
                for txt in label_text_objects:
                    if numeric_size is not None:
                        txt.set_fontsize(numeric_size)
                    if fam_chain:
                        txt.set_fontfamily(fam_chain[0])
                for axis_label in (ax.xaxis.label, ax.yaxis.label):
                    if numeric_size is not None:
                        axis_label.set_fontsize(numeric_size)
                    if fam_chain:
                        axis_label.set_fontfamily(fam_chain[0])
                for lbl in ax.get_xticklabels() + ax.get_yticklabels():
                    if numeric_size is not None:
                        lbl.set_fontsize(numeric_size)
                    if fam_chain:
                        lbl.set_fontfamily(fam_chain[0])

            # ---- Tick visibility + widths ----
            ticks_cfg = cfg.get("ticks", {})
            vis_cfg = ticks_cfg.get("visibility", {})
            changed_visibility = False
            for k, v in vis_cfg.items():
                if k in tick_state and isinstance(v, bool):
                    tick_state[k] = v
                    changed_visibility = True
            if changed_visibility:
                update_tick_visibility()

            xmaj = ticks_cfg.get("x_major_width")
            xminr = ticks_cfg.get("x_minor_width")
            ymaj = ticks_cfg.get("y_major_width")
            yminr = ticks_cfg.get("y_minor_width")
            if any(v is not None for v in (xmaj, xminr, ymaj, yminr)):
                if xmaj is not None:
                    ax.tick_params(axis='x', which='major', width=xmaj)
                if xminr is not None:
                    ax.tick_params(axis='x', which='minor', width=xminr)
                if ymaj is not None:
                    ax.tick_params(axis='y', which='major', width=ymaj)
                if yminr is not None:
                    ax.tick_params(axis='y', which='minor', width=yminr)

            # ---- Spines (width only) ----
            for name, sp_dict in cfg.get("spines", {}).items():
                if name in ax.spines:
                    if "linewidth" in sp_dict:
                        ax.spines[name].set_linewidth(sp_dict["linewidth"])
                    if "color" in sp_dict:
                        try:
                            ax.spines[name].set_edgecolor(sp_dict["color"])
                        except Exception:
                            pass
                    if "visible" in sp_dict:
                        ax.spines[name].set_visible(sp_dict["visible"])

            # ---- Lines (full style) ----
            for entry in cfg.get("lines", []):
                idx = entry.get("index")
                if idx is None or not (0 <= idx < len(ax.lines)):
                    continue
                ln = ax.lines[idx]
                if "color" in entry:
                    ln.set_color(entry["color"])
                if "linewidth" in entry:
                    ln.set_linewidth(entry["linewidth"])
                if "linestyle" in entry:
                    try: ln.set_linestyle(entry["linestyle"])
                    except Exception: pass
                if "marker" in entry:
                    try: ln.set_marker(entry["marker"])
                    except Exception: pass
                if "markersize" in entry:
                    try: ln.set_markersize(entry["markersize"])
                    except Exception: pass
                if "markerfacecolor" in entry:
                    try: ln.set_markerfacecolor(entry["markerfacecolor"])
                    except Exception: pass
                if "markeredgecolor" in entry:
                    try: ln.set_markeredgecolor(entry["markeredgecolor"])
                    except Exception: pass
                if "alpha" in entry and entry["alpha"] is not None:
                    try: ln.set_alpha(entry["alpha"])
                    except Exception: pass
                if False and "label" in entry and idx < len(labels):  # intentionally disabled
                    labels[idx] = entry["label"]
                    if idx < len(label_text_objects):
                        label_text_objects[idx].set_text(f"{idx+1}: {labels[idx]}")

            # ---- CIF tick sets (labels & colors) ----
            cif_cfg = cfg.get("cif_ticks", [])
            if cif_cfg and cif_tick_series:
                for entry in cif_cfg:
                    idx = entry.get("index")
                    if idx is None: continue
                    if 0 <= idx < len(cif_tick_series):
                        lab,fname,peaksQ,wl,qmax_sim,color_old = cif_tick_series[idx]
                        lab_new = entry.get("label", lab)
                        color_new = entry.get("color", color_old)
                        cif_tick_series[idx] = (lab_new, fname, peaksQ, wl, qmax_sim, color_new)
                if hasattr(ax,'_cif_draw_func'):
                    try: ax._cif_draw_func()
                    except Exception: pass

            # ---- Label layout handling ----
            layout_cfg = cfg.get("layout", {})
            cfg_layout = layout_cfg.get("label_layout")
            if cfg_layout == "block_top_right" and not args.stack:
                update_labels(ax, y_data_list, label_text_objects, False)
            elif cfg_layout == "stack" and not args.stack:
                print("Warning: Style file was created in stacked mode; current plot not stacked. Labels kept in block layout.")
            else:
                update_labels(ax, y_data_list, label_text_objects, args.stack)

            # NEW: re-run margin logic after size change & label update
            try:
                adjust_margins()
            except Exception:
                pass
            #try:
            #    ensure_text_visibility()
            except Exception:
                pass

            fig.canvas.draw_idle()
            print(f"Applied style (size, dpi, axes labels, font, ticks, lines, layout) from {filename}")
            # Reapply axis title toggle state if present
            try:
                at_cfg = cfg.get('axis_titles', {})
                # Top X title
                if at_cfg.get('top_x') and not getattr(ax,'_top_xlabel_on', False) and ax.get_xlabel():
                    txt = ax.xaxis.get_label(); txt.set_position((0.5,1.02)); txt.set_verticalalignment('bottom'); ax._top_xlabel_on = True
                if not at_cfg.get('top_x') and getattr(ax,'_top_xlabel_on', False):
                    txt = ax.xaxis.get_label(); txt.set_position((0.5,-0.12)); txt.set_verticalalignment('top'); ax._top_xlabel_on = False
                # Bottom X presence
                if not at_cfg.get('has_bottom_x', True):
                    ax.set_xlabel("")
                elif at_cfg.get('has_bottom_x', True) and not ax.get_xlabel():
                    if hasattr(ax,'_stored_xlabel'): ax.set_xlabel(ax._stored_xlabel)
                # Right Y duplicate
                if at_cfg.get('right_y') and not getattr(ax,'_right_ylabel_on', False):
                    if not hasattr(ax,'_right_label_axis') or ax._right_label_axis is None:
                        ax._right_label_axis = ax.twinx(); ax._right_label_axis.set_frame_on(False); ax._right_label_axis.tick_params(which='both', length=0, labelleft=False, labelright=False)
                    ax._right_label_axis.set_ylabel(ax.get_ylabel()); ax._right_ylabel_on = True
                if not at_cfg.get('right_y') and getattr(ax,'_right_ylabel_on', False):
                    if hasattr(ax,'_right_label_axis') and ax._right_label_axis is not None:
                        ax._right_label_axis.set_ylabel("")
                    ax._right_ylabel_on = False
                # Left Y presence
                if not at_cfg.get('has_left_y', True):
                    ax.set_ylabel("")
                elif at_cfg.get('has_left_y', True) and not ax.get_ylabel():
                    if hasattr(ax,'_stored_ylabel'): ax.set_ylabel(ax._stored_ylabel)
                fig.canvas.draw_idle()
            except Exception:
                pass
        except Exception as e:
            print(f"Error applying config: {e}")

    # Initialize with current defaults
    update_tick_visibility()

    # --- Crosshair state & toggle function (UPDATED) ---
    crosshair = {
        'active': False,
        'hline': None,
        'vline': None,
        'text': None,
        'cid_motion': None,
        'wavelength': None  # only used when axis is 2theta
    }

    def toggle_crosshair():
        if not crosshair['active']:
            if not use_Q:
                try:
                    wl_in = input("Enter wavelength in Å for Q,d display (blank=skip, q=cancel): ").strip()
                    if wl_in.lower() == 'q':
                        print("Canceled.")
                        return
                    if wl_in:
                        crosshair['wavelength'] = float(wl_in)
                    else:
                        crosshair['wavelength'] = None
                except ValueError:
                    print("Invalid wavelength. Skipping Q,d calculation.")
                    crosshair['wavelength'] = None
            vline = ax.axvline(x=ax.get_xlim()[0], color='0.35', ls='--', lw=0.8, alpha=0.85, zorder=9999)
            hline = ax.axhline(y=ax.get_ylim()[0], color='0.35', ls='--', lw=0.8, alpha=0.85, zorder=9999)
            txt = ax.text(1.0, 1.0, "",
                          ha='right', va='bottom',
                          transform=ax.transAxes,
                          fontsize=max(9, int(0.6 * plt.rcParams.get('font.size', 12))),
                          color='0.15',
                          bbox=dict(boxstyle='round,pad=0.25', fc='white', ec='0.7', alpha=0.8))

            def on_move(event):
                if event.inaxes != ax or event.xdata is None or event.ydata is None:
                    return
                x = float(event.xdata)
                y = float(event.ydata)
                vline.set_xdata([x, x])
                hline.set_ydata([y, y])

                if use_Q:
                    Q = x
                    if Q != 0:
                        d = 2 * np.pi / Q
                        txt.set_text(f"Q={Q:.6g}\nd={d:.6g} Å\ny={y:.6g}")
                    else:
                        txt.set_text(f"Q={Q:.6g}\nd=∞\ny={y:.6g}")
                elif use_r:
                    txt.set_text(f"r={x:.6g} Å\ny={y:.6g}")
                else:
                    # 2θ mode
                    if crosshair['wavelength'] is not None:
                        lam = crosshair['wavelength']
                        theta_rad = np.radians(x / 2.0)
                        Q = 4 * np.pi * np.sin(theta_rad) / lam
                        if Q != 0:
                            d = 2 * np.pi / Q
                            txt.set_text(f"2θ={x:.6g}°\nQ={Q:.6g}\nd={d:.6g} Å\ny={y:.6g}")
                        else:
                            txt.set_text(f"2θ={x:.6g}°\nQ=0\nd=∞\ny={y:.6g}")
                    else:
                        txt.set_text(f"2θ={x:.6g}°\ny={y:.6g}")

                fig.canvas.draw_idle()

            cid = fig.canvas.mpl_connect('motion_notify_event', on_move)
            crosshair.update({'active': True, 'hline': hline, 'vline': vline,
                              'text': txt, 'cid_motion': cid})
            print("Crosshair ON. Move mouse over axes. Press 'n' again to turn off.")
        else:
            if crosshair['cid_motion'] is not None:
                fig.canvas.mpl_disconnect(crosshair['cid_motion'])
            for k in ('hline', 'vline', 'text'):
                art = crosshair[k]
                if art is not None:
                    try:
                        art.remove()
                    except Exception:
                        pass
            crosshair.update({'active': False, 'hline': None, 'vline': None,
                              'text': None, 'cid_motion': None})
            fig.canvas.draw_idle()
            print("Crosshair OFF.")
    # --- End crosshair additions (UPDATED) ---

    # -------- Session save/load helpers (NEW) --------
    SESSION_VERSION = 2  # incremented for axis_mode, label_layout, CIF maps
    def _session_dump(filename):
        try:
            # Infer axis mode string
            if use_Q:
                axis_mode_session = 'Q'
            elif use_r:
                axis_mode_session = 'r'
            elif use_E:
                axis_mode_session = 'energy'
            elif use_k:
                axis_mode_session = 'k'
            elif use_rft:
                axis_mode_session = 'rft'
            elif 'use_2th' in globals() and use_2th:
                axis_mode_session = '2theta'
            else:
                axis_mode_session = 'unknown'
            label_layout = 'stack' if args.stack else 'block'
            # Axes frame size (in inches) for clarity (canvas stays fixed if keep_canvas_fixed=True)
            bbox = ax.get_position()
            fw, fh = fig.get_size_inches()
            frame_w_in = bbox.width * fw
            frame_h_in = bbox.height * fh
            # Save spine visibility
            spine_vis = {name: sp.get_visible() for name, sp in ax.spines.items()}
            sess = {
                'version': SESSION_VERSION,
                'x_data': [np.array(a) for a in x_data_list],
                'y_data': [np.array(a) for a in y_data_list],
                'orig_y': [np.array(a) for a in orig_y],
                'offsets': list(offsets_list),
                'labels': list(labels),
                'line_styles': [
                    {
                        'color': ln.get_color(),
                        'linewidth': ln.get_linewidth(),
                        'linestyle': ln.get_linestyle(),
                        'alpha': ln.get_alpha(),
                        'marker': ln.get_marker(),
                        'markersize': ln.get_markersize(),
                        'markerfacecolor': ln.get_markerfacecolor(),
                        'markeredgecolor': ln.get_markeredgecolor()
                    } for ln in ax.lines
                ],
                'delta': delta,
                'label_layout': label_layout,
                'axis_mode': axis_mode_session,
                'axis': {
                    'xlabel': ax.get_xlabel(),
                    'ylabel': ax.get_ylabel(),
                    'xlim': ax.get_xlim(),
                    'ylim': ax.get_ylim()
                },
                'figure': {
                    'size': tuple(map(float, fig.get_size_inches())),  # canvas size
                    'dpi': int(fig.dpi),
                    'frame_size': (frame_w_in, frame_h_in),
                    'margins': {
                        'left': float(bbox.x0),
                        'bottom': float(bbox.y0),
                        'right': float(bbox.x0 + bbox.width),
                        'top': float(bbox.y0 + bbox.height)
                    },
                    'spine_vis': spine_vis
                },
                'tick_state': tick_state.copy(),
                'font': {
                    'size': plt.rcParams.get('font.size'),
                    'chain': list(plt.rcParams.get('font.sans-serif', []))
                },
                'args_subset': {
                    'stack': bool(args.stack),
                    'autoscale': bool(args.autoscale),
                    'raw': bool(args.raw)
                },
                'cif_tick_series': [tuple(t) for t in cif_tick_series] if 'cif_tick_series' in globals() else None,
                'cif_hkl_map': {k: [tuple(v) for v in val] for k,val in cif_hkl_map.items()} if 'cif_hkl_map' in globals() else {},
                'cif_hkl_label_map': {k: dict(v) for k,v in cif_hkl_label_map.items()} if 'cif_hkl_label_map' in globals() else {},
                'show_cif_hkl': globals().get('show_cif_hkl', False)
            }
            # Axis title toggle state for session
            sess['axis_titles'] = {
                'top_x': bool(getattr(ax,'_top_xlabel_on', False)),
                'right_y': bool(getattr(ax,'_right_ylabel_on', False)),
                'has_bottom_x': bool(ax.get_xlabel()),
                'has_left_y': bool(ax.get_ylabel())
            }
            target = _confirm_overwrite(filename)
            if not target:
                print("Session save canceled.")
                return
            with open(target, 'wb') as f:
                pickle.dump(sess, f)
            print(f"Session saved to {target}")
        except Exception as e:
            print(f"Error saving session: {e}")

    def _session_load(filename):
        nonlocal delta
        try:
            with open(filename, 'rb') as f:
                sess = pickle.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
            return
        if not isinstance(sess, dict) or sess.get('version') not in (1, SESSION_VERSION):
            print("Unsupported or corrupt session file (version mismatch).")
            return
        try:
            # Clear axes
            ax.cla()
            # Basic arrays
            x_loaded = sess.get('x_data', [])
            y_loaded = sess.get('y_data', [])
            orig_loaded = sess.get('orig_y', [])
            offsets_loaded = sess.get('offsets', [])
            labels_loaded = sess.get('labels', [])
            delta = sess.get('delta', delta)
            saved_stack = bool(sess.get('args_subset', {}).get('stack', False))
            x_data_list[:] = [np.array(a) for a in x_loaded]
            offsets_list[:] = list(offsets_loaded) if offsets_loaded else [0.0]*len(x_data_list)
            # Reconstruct baseline (orig_y) and displayed (y_data_list) coherently.
            if orig_loaded and len(orig_loaded) == len(x_loaded):
                orig_y[:] = [np.array(a) for a in orig_loaded]
            else:
                # Fallback for older sessions: derive baseline by subtracting offset from stored y_data
                orig_y[:] = []
                for i, arr in enumerate(y_loaded):
                    off = offsets_list[i] if i < len(offsets_list) else 0.0
                    arr_np = np.array(arr)
                    orig_y.append(arr_np - off)
            # Now rebuild y_data_list from baseline + offsets to ensure consistency
            y_data_list[:] = []
            for i in range(len(orig_y)):
                off = offsets_list[i] if i < len(offsets_list) else 0.0
                y_plot = orig_y[i] + off
                y_data_list.append(y_plot)
            labels[:] = list(labels_loaded)
            # Provide full-range mirrors so range changes work after load
            x_full_list[:] = [a.copy() for a in x_data_list]
            raw_y_full_list[:] = [a.copy() for a in orig_y]
            # Re-draw lines
            for x_arr, y_arr in zip(x_data_list, y_data_list):
                ax.plot(x_arr, y_arr, lw=1)
            # Restore axis mode (used by some interactive features like CIF conversions)
            axis_mode_loaded = sess.get('axis_mode') or sess.get('axis', {}).get('mode')
            try:
                axis_mode_local = axis_mode_loaded if axis_mode_loaded else 'unknown'
            except Exception:
                axis_mode_local = 'unknown'
            # Apply stored line styles if present
            try:
                stored_styles = sess.get('line_styles', [])
                for ln, st in zip(ax.lines, stored_styles):
                    if 'color' in st: ln.set_color(st['color'])
                    if 'linewidth' in st: ln.set_linewidth(st['linewidth'])
                    if 'linestyle' in st:
                        try: ln.set_linestyle(st['linestyle'])
                        except Exception: pass
                    if 'alpha' in st and st['alpha'] is not None: ln.set_alpha(st['alpha'])
                    if 'marker' in st and st['marker'] is not None:
                        try: ln.set_marker(st['marker'])
                        except Exception: pass
                    if 'markersize' in st and st['markersize'] is not None:
                        try: ln.set_markersize(st['markersize'])
                        except Exception: pass
                    if 'markerfacecolor' in st and st['markerfacecolor'] is not None:
                        try: ln.set_markerfacecolor(st['markerfacecolor'])
                        except Exception: pass
                    if 'markeredgecolor' in st and st['markeredgecolor'] is not None:
                        try: ln.set_markeredgecolor(st['markeredgecolor'])
                        except Exception: pass
            except Exception:
                pass
            # Restore figure size & dpi if present
            fig_cfg = sess.get('figure', {})
            # Restore spine visibility if present
            spine_vis = fig_cfg.get('spine_vis', {})
            for name, vis in spine_vis.items():
                if name in ax.spines:
                    ax.spines[name].set_visible(vis)
            try:
                if fig_cfg.get('size') and isinstance(fig_cfg['size'], (list, tuple)) and len(fig_cfg['size']) == 2:
                    fw, fh = fig_cfg['size']
                    if not globals().get('keep_canvas_fixed', True):
                        fig.set_size_inches(float(fw), float(fh), forward=True)
                    else:
                        print("(Canvas fixed) Ignoring session figure size restore.")
                if 'dpi' in fig_cfg:
                    try: fig.set_dpi(int(fig_cfg['dpi']))
                    except Exception: pass
            except Exception:
                pass
            # Restore axis labels/limits
            axis_cfg = sess.get('axis', {})
            if 'xlabel' in axis_cfg: ax.set_xlabel(axis_cfg['xlabel'])
            if 'ylabel' in axis_cfg: ax.set_ylabel(axis_cfg['ylabel'])
            if 'xlim' in axis_cfg: ax.set_xlim(*axis_cfg['xlim'])
            if 'ylim' in axis_cfg: ax.set_ylim(*axis_cfg['ylim'])
            # Tick state
            sess_tick = sess.get('tick_state', {})
            for k,v in sess_tick.items():
                if k in tick_state: tick_state[k] = v
            update_tick_visibility()
            # Font
            fnt = sess.get('font', {})
            try:
                if fnt.get('chain'):
                    plt.rcParams['font.family'] = 'sans-serif'
                    plt.rcParams['font.sans-serif'] = fnt['chain']
                if fnt.get('size'):
                    plt.rcParams['font.size'] = fnt['size']
            except Exception:
                pass
            # CIF ticks
            if sess.get('cif_tick_series') is not None and 'cif_tick_series' in globals():
                try:
                    cif_tick_series[:] = [tuple(t) for t in sess['cif_tick_series']]
                    globals()['show_cif_hkl'] = bool(sess.get('show_cif_hkl', False))
                    # Restore hkl maps if provided
                    if sess.get('cif_hkl_map'):
                        cif_hkl_map.clear(); cif_hkl_map.update({k: [tuple(v) for v in val] for k,val in sess['cif_hkl_map'].items()})
                    if sess.get('cif_hkl_label_map'):
                        cif_hkl_label_map.clear(); cif_hkl_label_map.update(sess['cif_hkl_label_map'])
                    if hasattr(ax,'_cif_draw_func'):
                        ax._cif_draw_func()
                except Exception as e:
                    print(f"Warning restoring CIF ticks: {e}")
            # Rebuild label text objects
            label_text_objects.clear()
            for i, lab in enumerate(labels):
                txt = ax.text(1.0, 1.0, f"{i+1}: {lab}", ha='right', va='top', transform=ax.transAxes,
                              fontsize=plt.rcParams.get('font.size', 12))
                label_text_objects.append(txt)
            # Override args.stack with saved stack for label layout
            try:
                args.stack = saved_stack
            except Exception:
                pass
            update_labels(ax, y_data_list, label_text_objects, saved_stack)
            # Restore axis title toggle states if stored
            try:
                at_cfg = sess.get('axis_titles', {})
                if at_cfg.get('top_x') and not getattr(ax,'_top_xlabel_on', False) and ax.get_xlabel():
                    txt = ax.xaxis.get_label(); txt.set_position((0.5,1.02)); txt.set_verticalalignment('bottom'); ax._top_xlabel_on = True
                if not at_cfg.get('has_bottom_x', True):
                    ax.set_xlabel("")
                if at_cfg.get('right_y') and not getattr(ax,'_right_ylabel_on', False):
                    if not hasattr(ax,'_right_label_axis') or ax._right_label_axis is None:
                        ax._right_label_axis = ax.twinx(); ax._right_label_axis.set_frame_on(False); ax._right_label_axis.tick_params(which='both', length=0, labelleft=False, labelright=False)
                    ax._right_label_axis.set_ylabel(ax.get_ylabel()); ax._right_ylabel_on = True
                if not at_cfg.get('has_left_y', True):
                    ax.set_ylabel("")
                fig.canvas.draw_idle()
            except Exception:
                pass
            fig.canvas.draw_idle()
            print(f"Session loaded from {filename}")
        except Exception as e:
            print(f"Error restoring session: {e}")
    # -------- End session helpers --------

    
    # history management:
    state_history = []

    def push_state(note=""):
        """Snapshot current editable state (before a modifying action)."""
        try:
            # Helper to capture a representative tick line width
            def _tick_width(axis, which):
                try:
                    ticks = axis.get_major_ticks() if which=='major' else axis.get_minor_ticks()
                    for t in ticks:
                        ln = t.tick1line
                        if ln.get_visible():
                            return ln.get_linewidth()
                except Exception:
                    return None
                return None
            snap = {
                "note": note,
                "xlim": ax.get_xlim(),
                "ylim": ax.get_ylim(),
                "tick_state": tick_state.copy(),
                "font_size": plt.rcParams.get('font.size'),
                "font_chain": list(plt.rcParams.get('font.sans-serif', [])),
                "labels": list(labels),
                "delta": delta,
                "lines": [],
                "fig_size": list(fig.get_size_inches()),
                "fig_dpi": fig.dpi,
                "axes_bbox": [float(v) for v in ax.get_position().bounds],  # x0,y0,w,h
                "axis_labels": {"xlabel": ax.get_xlabel(), "ylabel": ax.get_ylabel()},
                "spines": {name: {"lw": sp.get_linewidth(), "color": sp.get_edgecolor()} for name, sp in ax.spines.items()},
                "tick_widths": {
                    "x_major": _tick_width(ax.xaxis, 'major'),
                    "x_minor": _tick_width(ax.xaxis, 'minor'),
                    "y_major": _tick_width(ax.yaxis, 'major'),
                    "y_minor": _tick_width(ax.yaxis, 'minor')
                },
                "cif_tick_series": [tuple(entry) for entry in cif_tick_series] if 'cif_tick_series' in globals() else None,
                "show_cif_hkl": globals().get('show_cif_hkl', False)
            }
            # Line + data arrays
            for i, ln in enumerate(ax.lines):
                snap["lines"].append({
                    "index": i,
                    "x": np.array(ln.get_xdata(), copy=True),
                    "y": np.array(ln.get_ydata(), copy=True),
                    "color": ln.get_color(),
                    "lw": ln.get_linewidth(),
                    "ls": ln.get_linestyle(),
                    "marker": ln.get_marker(),
                    "markersize": getattr(ln, 'get_markersize', lambda: None)(),
                    "mfc": getattr(ln, 'get_markerfacecolor', lambda: None)(),
                    "mec": getattr(ln, 'get_markeredgecolor', lambda: None)(),
                    "alpha": ln.get_alpha()
                })
            # Data lists
            snap["x_data_list"] = [np.array(a, copy=True) for a in x_data_list]
            snap["y_data_list"] = [np.array(a, copy=True) for a in y_data_list]
            snap["orig_y"]      = [np.array(a, copy=True) for a in orig_y]
            snap["offsets"]     = list(offsets_list)
            # Label text content
            snap["label_texts"] = [t.get_text() for t in label_text_objects]
            state_history.append(snap)
            # Cap history length
            if len(state_history) > 40:
                state_history.pop(0)
        except Exception as e:
            print(f"Warning: could not snapshot state: {e}")

    def restore_state():
        nonlocal delta
        if not state_history:
            print("No undo history.")
            return
        snap = state_history.pop()
        try:
            # Basic numeric state
            ax.set_xlim(*snap["xlim"])
            ax.set_ylim(*snap["ylim"])
            # Tick state
            for k, v in snap["tick_state"].items():
                if k in tick_state:
                    tick_state[k] = v
            update_tick_visibility()

            # Fonts
            if snap["font_chain"]:
                plt.rcParams['font.family'] = 'sans-serif'
                plt.rcParams['font.sans-serif'] = snap["font_chain"]
            if snap["font_size"]:
                try:
                    plt.rcParams['font.size'] = snap["font_size"]
                except Exception:
                    pass

            # Figure size & dpi
            if snap.get("fig_size") and isinstance(snap["fig_size"], (list, tuple)) and len(snap["fig_size"])==2:
                if not globals().get('keep_canvas_fixed', True):
                    try:
                        fig.set_size_inches(snap["fig_size"][0], snap["fig_size"][1], forward=True)
                    except Exception:
                        pass
                else:
                    print("(Canvas fixed) Ignoring undo figure size restore.")
            if snap.get("fig_dpi"):
                try:
                    fig.set_dpi(int(snap["fig_dpi"]))
                except Exception:
                    pass
            # Restore axes (plot frame) via stored bbox if present
            if snap.get("axes_bbox") and isinstance(snap["axes_bbox"], (list, tuple)) and len(snap["axes_bbox"])==4:
                try:
                    x0,y0,w,h = snap["axes_bbox"]
                    left = x0; bottom = y0; right = x0 + w; top = y0 + h
                    if 0 < left < right <=1 and 0 < bottom < top <=1:
                        fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
                except Exception:
                    pass

            # Axis labels
            axis_labels = snap.get("axis_labels", {})
            if axis_labels.get("xlabel") is not None:
                ax.set_xlabel(axis_labels["xlabel"])
            if axis_labels.get("ylabel") is not None:
                ax.set_ylabel(axis_labels["ylabel"])

            # Spines
            for name, spec in snap.get("spines", {}).items():
                sp_obj = ax.spines.get(name)
                if sp_obj is None: continue
                try:
                    if "lw" in spec:
                        sp_obj.set_linewidth(spec["lw"])
                    if "color" in spec and spec["color"] is not None:
                        sp_obj.set_edgecolor(spec["color"])
                except Exception:
                    pass

            # Tick widths
            tw = snap.get("tick_widths", {})
            try:
                if tw.get("x_major") is not None:
                    ax.tick_params(axis='x', which='major', width=tw["x_major"])
                if tw.get("x_minor") is not None:
                    ax.tick_params(axis='x', which='minor', width=tw["x_minor"])
                if tw.get("y_major") is not None:
                    ax.tick_params(axis='y', which='major', width=tw["y_major"])
                if tw.get("y_minor") is not None:
                    ax.tick_params(axis='y', which='minor', width=tw["y_minor"])
            except Exception:
                pass

            # Labels list
            labels[:] = snap["labels"]

            # Data & lines
            if len(snap["lines"]) == len(ax.lines):
                for item in snap["lines"]:
                    i = item["index"]
                    ln = ax.lines[i]
                    ln.set_data(item["x"], item["y"])
                    ln.set_color(item["color"])
                    ln.set_linewidth(item["lw"])
                    ln.set_linestyle(item["ls"])
                    if item["marker"] is not None:
                        ln.set_marker(item["marker"])
                    if item.get("markersize") is not None:
                        try: ln.set_markersize(item["markersize"])
                        except Exception: pass
                    if item.get("mfc") is not None:
                        try: ln.set_markerfacecolor(item["mfc"])
                        except Exception: pass
                    if item.get("mec") is not None:
                        try: ln.set_markeredgecolor(item["mec"])
                        except Exception: pass
                    if item["alpha"] is not None:
                        ln.set_alpha(item["alpha"])

            # Replace lists
            x_data_list[:] = [np.array(a, copy=True) for a in snap["x_data_list"]]
            y_data_list[:] = [np.array(a, copy=True) for a in snap["y_data_list"]]
            orig_y[:]      = [np.array(a, copy=True) for a in snap["orig_y"]]
            offsets_list[:] = list(snap["offsets"])
            delta = snap.get("delta", delta)

            # CIF tick sets & label visibility
            if snap.get("cif_tick_series") is not None and 'cif_tick_series' in globals():
                try:
                    cif_tick_series[:] = [tuple(t) for t in snap["cif_tick_series"]]
                except Exception:
                    pass
            if 'show_cif_hkl' in snap:
                try:
                    globals()['show_cif_hkl'] = snap['show_cif_hkl']
                except Exception:
                    pass
            # Redraw CIF ticks after restoration if available
            if hasattr(ax, '_cif_draw_func'):
                try:
                    ax._cif_draw_func()
                except Exception:
                    pass

            # Restore label texts (keep numbering style)
            for i, txt in enumerate(label_text_objects):
                base = labels[i] if i < len(labels) else ""
                txt.set_text(f"{i+1}: {base}")

            update_labels(ax, y_data_list, label_text_objects, args.stack)
            fig.canvas.draw_idle()
            print("Undo: restored previous state.")
        except Exception as e:
            print(f"Error restoring state: {e}")


    while True:
        print_main_menu()
        key = input("Press a key: ")


        # NEW: disable 'y' and 'd' in stack mode
        if args.stack and key in ('y', 'd'):
            print("Option disabled in --stack mode.")
            continue

        if key == 'q':
            confirm = input("Quit interactive session? Remember to save the plot! (y/n): ").strip().lower()
            if confirm == 'y':
                break
            else:
                continue
        elif key == 'z':  # toggle hkl labels on CIF ticks (non-blocking)
            try:
                if not cif_tick_series:
                    print("No CIF ticks loaded.")
                    continue
                global show_cif_hkl, cif_extend_suspended
                # Flip visibility flag
                show_cif_hkl = not globals().get('show_cif_hkl', False)
                # Avoid re-entrant extension while redrawing
                prev_ext = cif_extend_suspended
                cif_extend_suspended = True
                if hasattr(ax, '_cif_draw_func'):
                    ax._cif_draw_func()
                cif_extend_suspended = prev_ext
                # Count visible labels (quick heuristic: text objects containing '(' )
                n_labels = 0
                if show_cif_hkl and hasattr(ax, '_cif_tick_art'):
                    for art in ax._cif_tick_art:
                        try:
                            if hasattr(art, 'get_text') and '(' in art.get_text():
                                n_labels += 1
                        except Exception:
                            pass
                print(f"CIF hkl labels {'ON' if show_cif_hkl else 'OFF'} (visible labels: {n_labels}).")
            except Exception as e:
                print(f"Error toggling hkl labels: {e}")
            continue
        elif key == 'b':  # <-- UNDO
            restore_state()
            continue
        elif key == 'n':
            if not is_diffraction:
                print("Crosshair disabled for non-diffraction data (allowed only for 2θ or Q).")
                continue
            try:
                toggle_crosshair()
            except Exception as e:
                print(f"Error toggling crosshair: {e}")
            continue
        elif key == 's':
            # Save current interactive session
            fname = input("Save session filename (default 'batplot_session.pkl', q=cancel): ").strip()
            if not fname or fname.lower() == 'q':
                print("Canceled.")
                continue
            if not os.path.splitext(fname)[1]:
                fname += '.pkl'
            _session_dump(fname)
            continue
        elif key == 'w':  # hidden game remains on 'i'
            play_jump_game(); continue
        elif key == 'c':
            try:
                has_cif = False
                try:
                    has_cif = any(f.lower().endswith('.cif') for f in args.files)
                except Exception:
                    pass
                while True:
                    print("Color menu:")
                    print("  m : manual color mapping  (e.g., 1:red 2:#00B006)")
                    print("  p : apply colormap palette to a range (e.g., 1-3 viridis)")
                    if has_cif and cif_tick_series:
                        print("  t : change CIF tick set color (e.g., 1:red 2:#888888)")
                    print("  q : return to main menu")
                    sub = input("Choose (m/p/t/q): ").strip().lower()
                    if sub == 'q':
                        break
                    if sub == '':
                        continue
                    if sub == 'm':
                        print("Current curves (q to cancel):")
                        for idx, label in enumerate(labels):
                            print(f"{idx+1}: {label}")
                        color_input = input("Enter colors (e.g., 1:red 2:#00B006) or q: ").strip()
                        if not color_input or color_input.lower() == 'q':
                            print("Canceled.")
                        else:
                            push_state("color-manual")
                            entries = color_input.split()
                            for entry in entries:
                                if ":" not in entry:
                                    print(f"Skip malformed token: {entry}")
                                    continue
                                idx_str, color = entry.split(":", 1)
                                try:
                                    i = int(idx_str) - 1
                                    if 0 <= i < len(ax.lines):
                                        ax.lines[i].set_color(color)
                                    else:
                                        print(f"Index out of range: {idx_str}")
                                except ValueError:
                                    print(f"Bad index: {idx_str}")
                        fig.canvas.draw()
                    elif sub == 't' and has_cif and cif_tick_series:
                        print("Current CIF tick sets:")
                        for i,(lab,_,_,_,_,color) in enumerate(cif_tick_series):
                            print(f"  {i+1}: {lab} (color {color})")
                        line = input("Enter mappings (e.g., 1:red 2:#555555) or q: ").strip()
                        if not line or line.lower()=='q':
                            print("Canceled.")
                        else:
                            mappings = line.split()
                            for token in mappings:
                                if ':' not in token:
                                    print(f"Skip malformed token: {token}")
                                    continue
                                idx_s, col = token.split(':',1)
                                try:
                                    idx_i = int(idx_s)-1
                                    if 0 <= idx_i < len(cif_tick_series):
                                        lab,fname,peaksQ,wl,qmax_sim,_c = cif_tick_series[idx_i]
                                        cif_tick_series[idx_i] = (lab,fname,peaksQ,wl,qmax_sim,col)
                                    else:
                                        print(f"Index out of range: {idx_s}")
                                except ValueError:
                                    print(f"Bad index: {idx_s}")
                            if hasattr(ax,'_cif_draw_func'):
                                ax._cif_draw_func()
                        fig.canvas.draw()
                    elif sub == 'p':
                        base_palettes = ['viridis', 'plasma', 'inferno', 'magma', 'batlow']
                        extras = []
                        if 'turbo' in plt.colormaps():
                            extras.append('turbo')
                        if 'batlowK' in plt.colormaps():
                            extras.append('batlowK')
                        print("Common perceptually uniform palettes:")
                        print("  " + ", ".join(base_palettes + extras[:2]))
                        print("Example: 1-4 viridis   or: all magma_r   or: 1-3,5 plasma, _r for reverse")
                        line = input("Enter range(s) and palette (e.g., '1-3 viridis') or q: ").strip()
                        if not line or line.lower() == 'q':
                            print("Canceled.")
                        else:
                            parts = line.split()
                            if len(parts) < 2:
                                print("Need range(s) and palette.")
                            else:
                                palette_name = parts[-1]
                                range_part = " ".join(parts[:-1]).replace(" ", "")
                                def parse_ranges(spec, total):
                                    spec = spec.lower()
                                    if spec == 'all':
                                        return list(range(total))
                                    result = set()
                                    tokens = spec.split(',')
                                    for tok in tokens:
                                        if not tok:
                                            continue
                                        if '-' in tok:
                                            try:
                                                a, b = tok.split('-', 1)
                                                start = int(a) - 1
                                                end = int(b) - 1
                                                if start > end:
                                                    start, end = end, start
                                                for i in range(start, end + 1):
                                                    if 0 <= i < total:
                                                        result.add(i)
                                            except ValueError:
                                                print(f"Bad range token: {tok}")
                                        else:
                                            try:
                                                i = int(tok) - 1
                                                if 0 <= i < total:
                                                    result.add(i)
                                                else:
                                                    print(f"Index out of range: {tok}")
                                            except ValueError:
                                                print(f"Bad index token: {tok}")
                                    return sorted(result)
                                indices = parse_ranges(range_part, len(ax.lines))
                                if not indices:
                                    print("No valid indices parsed.")
                                else:
                                    try:
                                        cmap = plt.get_cmap(palette_name)
                                    except ValueError:
                                        cmap = None
                                    if cmap is None and palette_name.lower().startswith("batlow"):
                                        try:
                                            import importlib
                                            cmc = importlib.import_module('cmcrameri.cm')
                                            attr = palette_name.lower()
                                            if hasattr(cmc, attr):
                                                cmap = getattr(cmc, attr)
                                            elif hasattr(cmc, 'batlow'):
                                                cmap = getattr(cmc, 'batlow')
                                        except Exception:
                                            pass
                                    if cmap is None:
                                        print(f"Unknown colormap '{palette_name}'.")
                                    else:
                                        push_state("color-palette")
                                        nsel = len(indices)
                                        low_clip = 0.08
                                        high_clip = 0.85
                                        if nsel == 1:
                                            colors = [cmap(0.55)]
                                        elif nsel == 2:
                                            colors = [cmap(low_clip), cmap(high_clip)]
                                        else:
                                            positions = np.linspace(low_clip, high_clip, nsel)
                                            colors = [cmap(p) for p in positions]
                                        for c_idx, line_idx in enumerate(indices):
                                            ax.lines[line_idx].set_color(colors[c_idx])
                                        fig.canvas.draw()
                                        print(f"Applied '{palette_name}' to curves: " +
                                              ", ".join(str(i+1) for i in indices))
                    else:
                        print("Unknown color submenu option.")
            except Exception as e:
                print(f"Error in color menu: {e}")
        elif key == 'r':
            try:
                has_cif = False
                try:
                    has_cif = any(f.lower().endswith('.cif') for f in args.files)
                except Exception:
                    pass
                while True:
                    rename_opts = "c=curve"
                    if has_cif:
                        rename_opts += ", t=cif tick label"
                    rename_opts += ", x=x-axis, y=y-axis, q=return"
                    mode = input(f"Rename ({rename_opts}): ").strip().lower()
                    if mode == 'q':
                        break
                    if mode == '':
                        continue
                    if mode == 'c':
                        idx_in = input("Curve number to rename (q=cancel): ").strip()
                        if not idx_in or idx_in.lower() == 'q':
                            print("Canceled.")
                            continue
                        try:
                            idx = int(idx_in) - 1
                        except ValueError:
                            print("Invalid index.")
                            continue
                        if not (0 <= idx < len(labels)):
                            print("Invalid index.")
                            continue
                        new_label = input("New curve label (q=cancel): ").strip()
                        if not new_label or new_label.lower() == 'q':
                            print("Canceled.")
                            continue
                        push_state("rename-curve")
                        labels[idx] = new_label
                        label_text_objects[idx].set_text(f"{idx+1}: {new_label}")
                        fig.canvas.draw()
                    elif mode == 't':
                        if not cif_tick_series:
                            print("No CIF tick sets to rename.")
                            continue
                        for i,(lab, fname, *_rest) in enumerate(cif_tick_series):
                            print(f"  {i+1}: {lab} ({os.path.basename(fname)})")
                        s = input("CIF tick number to rename (q=cancel): ").strip()
                        if not s or s.lower()=='q':
                            print("Canceled.")
                            continue
                        try:
                            idx = int(s)-1
                            if not (0 <= idx < len(cif_tick_series)):
                                print("Index out of range."); continue
                        except ValueError:
                            print("Bad index."); continue
                        new_name = input("New CIF tick label (q=cancel): ").strip()
                        if not new_name or new_name.lower()=='q':
                            print("Canceled."); continue
                        lab,fname,peaksQ,wl,qmax_sim,color = cif_tick_series[idx]
                        cif_extend_suspended = True
                        if hasattr(ax, '_cif_tick_art'):
                            try:
                                for art in list(getattr(ax, '_cif_tick_art', [])):
                                    try:
                                        art.remove()
                                    except Exception:
                                        pass
                                ax._cif_tick_art = []
                            except Exception:
                                pass
                        cif_tick_series[idx] = (new_name, fname, peaksQ, wl, qmax_sim, color)
                        if hasattr(ax,'_cif_draw_func'): ax._cif_draw_func()
                        fig.canvas.draw()
                        cif_extend_suspended = False
                    elif mode in ('x','y'):
                        print("Enter new axis label (q=cancel). Prefer mathtext for superscripts:")
                        new_axis = input("New axis label: ").strip()
                        if not new_axis or new_axis.lower() == 'q':
                            print("Canceled.")
                            continue
                        new_axis = normalize_label_text(new_axis)
                        push_state("rename-axis")
                        if mode == 'x':
                            ax.set_xlabel(new_axis)
                        else:
                            ax.set_ylabel(new_axis)
                        sync_fonts()
                        fig.canvas.draw()
                    else:
                        print("Invalid choice.")
                    # loop continues until q
            except Exception as e:
                print(f"Error: {e}")
        elif key == 'a':
            try:
                if not args.stack:
                    print('Be careful, changing the arrangement may lead to a mess! If you want to rearrange the curves, use "--stack".')
                print("Current curve order:")
                for idx, label in enumerate(labels):
                    print(f"{idx+1}: {label}")
                new_order_str = input("Enter new order (space-separated indices, q=cancel): ").strip()
                if not new_order_str or new_order_str.lower() == 'q':
                    print("Canceled.")
                    continue
                new_order = [int(i)-1 for i in new_order_str.strip().split()]
                if len(new_order) != len(labels):
                    print("Error: Number of indices does not match number of curves.")
                    continue
                if any(i < 0 or i >= len(labels) for i in new_order):
                    print("Error: Invalid index in order list.")
                    continue

                push_state("rearrange")

                original_styles = []
                for ln in ax.lines:
                    original_styles.append({
                        "color": ln.get_color(),
                        "linewidth": ln.get_linewidth(),
                        "linestyle": ln.get_linestyle(),
                        "alpha": ln.get_alpha(),
                        "marker": ln.get_marker(),
                        "markersize": ln.get_markersize(),
                        "markerfacecolor": ln.get_markerfacecolor(),
                        "markeredgecolor": ln.get_markeredgecolor()
                    })
                reordered_styles = [original_styles[i] for i in new_order]
                xlim_current = ax.get_xlim()

                x_data_list[:]      = [x_data_list[i] for i in new_order]
                orig_y[:]           = [orig_y[i] for i in new_order]
                y_data_list[:]      = [y_data_list[i] for i in new_order]
                labels[:]           = [labels[i] for i in new_order]
                label_text_objects[:] = [label_text_objects[i] for i in new_order]
                x_full_list[:]      = [x_full_list[i] for i in new_order]
                raw_y_full_list[:]  = [raw_y_full_list[i] for i in new_order]
                offsets_list[:]     = [offsets_list[i] for i in new_order]

                if args.stack:
                    offset_local = 0.0
                    for i, (x_plot, y_norm, style) in enumerate(zip(x_data_list, orig_y, reordered_styles)):
                        y_plot_offset = y_norm + offset_local
                        y_data_list[i] = y_plot_offset
                        offsets_list[i] = offset_local
                        ln = ax.lines[i]
                        ln.set_data(x_plot, y_plot_offset)
                        ln.set_color(style["color"])
                        ln.set_linewidth(style["linewidth"])
                        ln.set_linestyle(style["linestyle"])
                        ln.set_alpha(style["alpha"])
                        ln.set_marker(style["marker"])
                        ln.set_markersize(style["markersize"])
                        ln.set_markerfacecolor(style["markerfacecolor"])
                        ln.set_markeredgecolor(style["markeredgecolor"])
                        y_range = (y_norm.max() - y_norm.min()) if y_norm.size else 0.0
                        gap = y_range + (delta * (y_range if args.autoscale else 1.0))
                        offset_local -= gap
                else:
                    offset_local = 0.0
                    for i, (x_plot, y_norm, style) in enumerate(zip(x_data_list, orig_y, reordered_styles)):
                        y_plot_offset = y_norm + offset_local
                        y_data_list[i] = y_plot_offset
                        offsets_list[i] = offset_local
                        ln = ax.lines[i]
                        ln.set_data(x_plot, y_plot_offset)
                        ln.set_color(style["color"])
                        ln.set_linewidth(style["linewidth"])
                        ln.set_linestyle(style["linestyle"])
                        ln.set_alpha(style["alpha"])
                        ln.set_marker(style["marker"])
                        ln.set_markersize(style["markersize"])
                        ln.set_markerfacecolor(style["markerfacecolor"])
                        ln.set_markeredgecolor(style["markeredgecolor"])
                        increment = (y_norm.max() - y_norm.min()) * delta if (args.autoscale and y_norm.size) else delta
                        offset_local += increment

                for i, (txt, lab) in enumerate(zip(label_text_objects, labels)):
                    txt.set_text(f"{i+1}: {lab}")
                ax.set_xlim(xlim_current)
                ax.set_xlabel(x_label)
                ax.set_ylabel("Intensity" if args.raw else "Normalized intensity (a.u.)")
                update_labels(ax, y_data_list, label_text_objects, args.stack)
                fig.canvas.draw()
            except Exception as e:
                print(f"Error rearranging curves: {e}")
        elif key == 'x':
            try:
                rng = input("Enter new X range (min max) or 'full' (q=cancel): ").strip()
                if not rng or rng.lower() == 'q':
                    print("Canceled.")
                    continue
                push_state("xrange")
                if rng.lower() == 'full':
                    new_min = min(xf.min() for xf in x_full_list if xf.size)
                    new_max = max(xf.max() for xf in x_full_list if xf.size)
                else:
                    new_min, new_max = map(float, rng.split())
                ax.set_xlim(new_min, new_max)
                for i in range(len(labels)):
                    xf = x_full_list[i]; yf_raw = raw_y_full_list[i]
                    mask = (xf>=new_min) & (xf<=new_max)
                    x_sub = xf[mask]; y_sub_raw = yf_raw[mask]
                    if x_sub.size == 0:
                        ax.lines[i].set_data([], [])
                        y_data_list[i] = np.array([]); orig_y[i] = np.array([]); continue
                    if not args.raw:
                        if y_sub_raw.size:
                            y_min = float(y_sub_raw.min())
                            y_max = float(y_sub_raw.max())
                            span = y_max - y_min
                            if span > 0:
                                y_sub_norm = (y_sub_raw - y_min) / span
                            else:
                                y_sub_norm = np.zeros_like(y_sub_raw)
                        else:
                            y_sub_norm = y_sub_raw
                    else:
                        y_sub_norm = y_sub_raw
                    offset_val = offsets_list[i]
                    y_with_offset = y_sub_norm + offset_val
                    ax.lines[i].set_data(x_sub, y_with_offset)
                    x_data_list[i] = x_sub
                    y_data_list[i] = y_with_offset
                    orig_y[i] = y_sub_norm
                ax.relim(); ax.autoscale_view(scalex=False, scaley=True)
                update_labels(ax, y_data_list, label_text_objects, args.stack)
                # Extend CIF ticks after x-range change
                try:
                    if hasattr(ax, '_cif_extend_func'):
                        ax._cif_extend_func(ax.get_xlim()[1])
                except Exception:
                    pass
                try:
                    if hasattr(ax, '_cif_draw_func'):
                        ax._cif_draw_func()
                except Exception:
                    pass
                #ensure_text_visibility()
                fig.canvas.draw()
            except Exception as e:
                print(f"Error setting X-axis range: {e}")
        elif key == 'y':  # <-- Y-RANGE HANDLER (now only reachable if not args.stack)
            try:
                rng = input("Enter new Y range (min max), 'auto', or 'full' (q=cancel): ").strip().lower()
                if not rng or rng == 'q':
                    print("Canceled.")
                    continue
                push_state("yrange")
                if rng == 'auto':
                    ax.relim()
                    ax.autoscale_view(scalex=False, scaley=True)
                else:
                    if rng == 'full':
                        all_min = None
                        all_max = None
                        for arr in y_data_list:
                            if arr.size:
                                mn = float(arr.min())
                                mx = float(arr.max())
                                all_min = mn if all_min is None else min(all_min, mn)
                                all_max = mx if all_max is None else max(all_max, mx)
                        if all_min is None or all_max is None:
                            print("No data to compute full Y range.")
                            continue
                        y_min, y_max = all_min, all_max
                    else:
                        parts = rng.split()
                        if len(parts) != 2:
                            print("Need exactly two numbers for Y range.")
                            continue
                        y_min, y_max = map(float, parts)
                        if y_min == y_max:
                            print("Warning: min == max; expanding slightly.")
                            eps = abs(y_min)*1e-6 if y_min != 0 else 1e-6
                            y_min -= eps
                            y_max += eps
                    ax.set_ylim(y_min, y_max)
                update_labels(ax, y_data_list, label_text_objects, args.stack)
                fig.canvas.draw_idle()
                print(f"Y range set to {ax.get_ylim()}")
            except Exception as e:
                print(f"Error setting Y-axis range: {e}")
        elif key == 'd':  # <-- DELTA / OFFSET HANDLER (now only reachable if not args.stack)
            if len(labels) <= 1:
                print("Warning: Only one curve loaded; applying an offset is not recommended.")
            try:
                new_delta_str = input(f"Enter new offset spacing (current={delta}): ").strip()
                new_delta = float(new_delta_str)
                delta = new_delta
                offsets_list[:] = []
                if args.stack:
                    # (Should not occur because disabled, but keep safe path)
                    current_offset = 0.0
                    for i, y_norm in enumerate(orig_y):
                        y_with_offset = y_norm + current_offset
                        y_data_list[i] = y_with_offset
                        offsets_list.append(current_offset)
                        ax.lines[i].set_data(x_data_list[i], y_with_offset)
                        y_range = (y_norm.max() - y_norm.min()) if y_norm.size else 0.0
                        gap = y_range + (delta * (y_range if args.autoscale else 1.0))
                        current_offset -= gap
                else:
                    current_offset = 0.0
                    for i, y_norm in enumerate(orig_y):
                        y_with_offset = y_norm + current_offset
                        y_data_list[i] = y_with_offset
                        offsets_list.append(current_offset)
                        ax.lines[i].set_data(x_data_list[i], y_with_offset)
                        increment = (y_norm.max() - y_norm.min()) * delta if (args.autoscale and y_norm.size) else delta
                        current_offset += increment
                update_labels(ax, y_data_list, label_text_objects, args.stack)
                ax.relim(); ax.autoscale_view(scalex=False, scaley=True)
                fig.canvas.draw()
                print(f"Offsets updated with delta={delta}")
            except Exception as e:
                print(f"Error updating offsets: {e}")
        elif key == 'l':
            try:
                while True:
                    print("Line submenu:")
                    print("  c  : change curve line widths")
                    print("  f  : change frame (axes spines) and tick widths")
                    print("  ld : show line and dots (markers) for all curves")
                    print("  d  : show only dots (no connecting line) for all curves")
                    print("  q  : return")
                    sub = input("Choose (c/f/ld/d/q): ").strip().lower()
                    if sub == 'q':
                        break
                    if sub == '':
                        continue
                    if sub == 'c':
                        spec = input("Curve widths (single value OR mappings like '1:1.2 3:2', q=cancel): ").strip()
                        if not spec or spec.lower() == 'q':
                            print("Canceled.")
                        else:
                            push_state("linewidth")
                            if ":" in spec:
                                parts = spec.split()
                                for p in parts:
                                    if ":" not in p:
                                        print(f"Skip malformed token: {p}")
                                        continue
                                    idx_str, lw_str = p.split(":", 1)
                                    try:
                                        idx = int(idx_str) - 1
                                        lw = float(lw_str)
                                        if 0 <= idx < len(ax.lines):
                                            ax.lines[idx].set_linewidth(lw)
                                        else:
                                            print(f"Index out of range: {idx+1}")
                                    except ValueError:
                                        print(f"Bad token: {p}")
                            else:
                                try:
                                    lw = float(spec)
                                    for ln in ax.lines:
                                        ln.set_linewidth(lw)
                                except ValueError:
                                    print("Invalid width value.")
                            fig.canvas.draw()
                    elif sub == 'f':
                        fw_in = input("Enter frame/tick width (e.g., 1.5) or 'm M' (major minor) or q: ").strip()
                        if not fw_in or fw_in.lower() == 'q':
                            print("Canceled.")
                        else:
                            push_state("framewidth")
                            parts = fw_in.split()
                            try:
                                if len(parts) == 1:
                                    frame_w = float(parts[0])
                                    tick_major = frame_w
                                    tick_minor = frame_w * 0.6
                                else:
                                    frame_w = float(parts[0])
                                    tick_major = float(parts[1])
                                    tick_minor = tick_major * 0.7
                                for sp in ax.spines.values():
                                    sp.set_linewidth(frame_w)
                                ax.tick_params(which='major', width=tick_major)
                                ax.tick_params(which='minor', width=tick_minor)
                                fig.canvas.draw()
                                print(f"Set frame width={frame_w}, major tick width={tick_major}, minor tick width={tick_minor}")
                            except ValueError:
                                print("Invalid numeric value(s).")
                    elif sub == 'ld':
                        push_state("line+dots")
                        try:
                            msize_in = input("Marker size (blank=auto ~3*lw): ").strip()
                            custom_msize = float(msize_in) if msize_in else None
                        except ValueError:
                            custom_msize = None
                        for ln in ax.lines:
                            lw = ln.get_linewidth() or 1.0
                            ln.set_linestyle('-')
                            ln.set_marker('o')
                            msize = custom_msize if custom_msize is not None else max(3.0, lw * 3.0)
                            ln.set_markersize(msize)
                            col = ln.get_color()
                            try:
                                ln.set_markerfacecolor(col)
                                ln.set_markeredgecolor(col)
                            except Exception:
                                pass
                        fig.canvas.draw()
                        print("Applied line+dots style to all curves.")
                    elif sub == 'd':
                        push_state("dots-only")
                        try:
                            msize_in = input("Marker size (blank=auto ~3*lw): ").strip()
                            custom_msize = float(msize_in) if msize_in else None
                        except ValueError:
                            custom_msize = None
                        for ln in ax.lines:
                            lw = ln.get_linewidth() or 1.0
                            ln.set_linestyle('None')
                            ln.set_marker('o')
                            msize = custom_msize if custom_msize is not None else max(3.0, lw * 3.0)
                            ln.set_markersize(msize)
                            col = ln.get_color()
                            try:
                                ln.set_markerfacecolor(col)
                                ln.set_markeredgecolor(col)
                            except Exception:
                                pass
                        fig.canvas.draw()
                        print("Applied dots-only style to all curves.")
                    else:
                        print("Unknown submenu option.")
            except Exception as e:
                print(f"Error setting widths: {e}")
        elif key == 'f':
            while True:
                subkey = input("Font submenu (s=size, f=family, q=return): ").strip().lower()
                if subkey == 'q':
                    break
                if subkey == '':
                    continue
                if subkey == 's':
                    try:
                        fs = input("Enter new font size (q=cancel): ").strip()
                        if not fs or fs.lower() == 'q':
                            print("Canceled.")
                        else:
                            push_state("font-change")
                            fs_val = float(fs)
                            apply_font_changes(new_size=fs_val)
                    except Exception as e:
                        print(f"Error changing font size: {e}")
                elif subkey == 'f':
                    try:
                        print("Common publication fonts:")
                        print("  1) Arial")
                        print("  2) Helvetica")
                        print("  3) Times New Roman")
                        print("  4) STIXGeneral")
                        print("  5) DejaVu Sans")
                        ft_raw = input("Enter font number or family name (q=cancel): ").strip()
                        if not ft_raw or ft_raw.lower() == 'q':
                            print("Canceled.")
                        else:
                            font_map = {
                                '1': 'Arial',
                                '2': 'Helvetica',
                                '3': 'Times New Roman',
                                '4': 'STIXGeneral',
                                '5': 'DejaVu Sans'
                            }
                            ft = font_map.get(ft_raw, ft_raw)
                            push_state("font-change")
                            print(f"Setting font family to: {ft}")
                            apply_font_changes(new_family=ft)
                    except Exception as e:
                        print(f"Error changing font family: {e}")
                else:
                    print("Invalid font submenu option.")
        elif key == 'g':
            try:
                while True:
                    choice = input("Resize submenu: (p=plot frame, c=canvas, q=cancel): ").strip().lower()
                    if not choice:
                        continue
                    if choice == 'q':
                        break
                    if choice == 'p':
                        push_state("resize-frame")
                        resize_plot_frame()
                        update_labels(ax, y_data_list, label_text_objects, args.stack)
                    elif choice == 'c':
                        push_state("resize-canvas")
                        resize_canvas()
                    else:
                        print("Unknown option.")
            except Exception as e:
                print(f"Error in resize submenu: {e}")
        elif key == 't':
            try:
                while True:
                    print("Toggle codes:")
                    print("  bx  bottom X major ticks & labels")
                    print("  tx  top    X major ticks & labels")
                    print("  ly  left   Y major ticks & labels")
                    print("  ry  right  Y major ticks & labels")
                    print("  mbx bottom X minor ticks")
                    print("  mtx top    X minor ticks")
                    print("  mly left   Y minor ticks")
                    print("  mry right  Y minor ticks")
                    print("  bt  bottom X axis title")
                    print("  tt  top    X axis title")
                    print("  lt  left   Y axis title")
                    print("  rt  right  Y axis title")
                    print("  bl  bottom plot frame line (spine)")
                    print("  tl  top    plot frame line (spine)")
                    print("  ll  left   plot frame line (spine)")
                    print("  rl  right  plot frame line (spine)")
                    print("  list show state   q return")
                    cmd = input("Enter code(s): ").strip().lower()
                    if not cmd:
                        continue
                    if cmd == 'q':
                        break
                    parts = cmd.split()
                    if parts == ['list']:
                        print_tick_state()
                        # Print spine (frame) visibility
                        print("Spine (frame) visibility:")
                        for spine in ['bottom','top','left','right']:
                            vis = get_spine_visible(spine)
                            print(f"  {spine:<6}: {'ON ' if vis else 'off'}")
                        continue
                    push_state("tick-toggle")
                    for p in parts:
                        # Axis title toggles
                        if p in ('bt','tt','lt','rt'):
                            if p == 'bt':
                                cur = ax.get_xlabel()
                                if cur:
                                    ax.set_xlabel("")
                                    print("Hid bottom X axis title")
                                else:
                                    ax.set_xlabel(ax._stored_xlabel if hasattr(ax,'_stored_xlabel') else ax.get_xlabel() or "")
                                    print("Shown bottom X axis title")
                            elif p == 'tt':
                                vis = getattr(ax, '_top_xlabel_on', False)
                                if not vis:
                                    lbl_text = ax.get_xlabel()
                                    if not lbl_text:
                                        print("No bottom X label to duplicate.")
                                    else:
                                        if not hasattr(ax,'_top_xlabel_artist') or ax._top_xlabel_artist is None:
                                            ax._top_xlabel_artist = ax.text(0.5,1.02,lbl_text,ha='center',va='bottom',transform=ax.transAxes)
                                        else:
                                            ax._top_xlabel_artist.set_text(lbl_text)
                                            ax._top_xlabel_artist.set_visible(True)
                                        ax._top_xlabel_on = True
                                        print("Shown duplicate top X axis title (bottom kept)")
                                else:
                                    if hasattr(ax,'_top_xlabel_artist') and ax._top_xlabel_artist is not None:
                                        ax._top_xlabel_artist.set_visible(False)
                                    ax._top_xlabel_on = False
                                    print("Hid top X axis title duplicate")
                            elif p == 'lt':
                                cur = ax.get_ylabel()
                                if cur:
                                    ax.set_ylabel("")
                                    print("Hid left Y axis title")
                                else:
                                    ax.set_ylabel(ax._stored_ylabel if hasattr(ax,'_stored_ylabel') else ax.get_ylabel() or "")
                                    print("Shown left Y axis title")
                            elif p == 'rt':
                                vis = getattr(ax, '_right_ylabel_on', False)
                                if not vis:
                                    base = ax.get_ylabel()
                                    if not base:
                                        print("No left Y label to duplicate.")
                                    else:
                                        if hasattr(ax,'_right_ylabel_artist') and ax._right_ylabel_artist is not None:
                                            try: ax._right_ylabel_artist.remove()
                                            except Exception: pass
                                        ax._right_ylabel_artist = ax.text(1.02,0.5,base, rotation=90, va='center', ha='left', transform=ax.transAxes)
                                        ax._right_ylabel_on = True
                                        print("Shown duplicate right Y axis title")
                                        position_right_ylabel()
                                else:
                                    if hasattr(ax,'_right_ylabel_artist') and ax._right_ylabel_artist is not None:
                                        try:
                                            ax._right_ylabel_artist.remove()
                                        except Exception:
                                            pass
                                        ax._right_ylabel_artist = None
                                    ax._right_ylabel_on = False
                                    print("Hid right Y axis title")
                            continue
                        # Plot frame (spine) toggles
                        if p in ('bl','tl','ll','rl'):
                            spine_map = {'bl':'bottom','tl':'top','ll':'left','rl':'right'}
                            spine = spine_map[p]
                            vis = get_spine_visible(spine)
                            set_spine_visible(spine, not vis)
                            print(f"Toggled {spine} spine -> {'ON' if not vis else 'off'}")
                            continue
                        # Tick toggles
                        if p in tick_state:
                            tick_state[p] = not tick_state[p]
                            print(f"Toggled {p} -> {'ON' if tick_state[p] else 'off'}")
                        else:
                            print(f"Unknown code: {p}")
                    update_tick_visibility(); update_labels(ax, y_data_list, label_text_objects, args.stack); sync_fonts(); position_top_xlabel(); position_right_ylabel()
            except Exception as e:
                print(f"Error in tick visibility menu: {e}")
        elif key == 'p':
            try:
                while True:
                    print_style_info()
                    sub = input("Style submenu: (e=export, q=return, r=refresh): ").strip().lower()
                    if sub == 'q':
                        break
                    if sub == 'r' or sub == '':
                        continue
                    if sub == 'e':
                        fname = input("Enter export filename (will add .bpcfg if missing, q=cancel): ").strip()
                        if not fname or fname.lower() == 'q':
                            print("Canceled.")
                        else:
                            export_style_config(fname)
                    else:
                        print("Unknown choice.")
            except Exception as e:
                print(f"Error in style submenu: {e}")
        elif key == 'i':
            try:
                fname = input("Enter style filename (.bpcfg, with or without extension, q=cancel): ").strip()
                if not fname or fname.lower() == 'q':
                    print("Canceled.")
                    continue
                if not os.path.isfile(fname):
                    root, ext = os.path.splitext(fname)
                    if ext == "":
                        alt = fname + ".bpcfg"
                        if os.path.isfile(alt):
                            fname = alt
                        else:
                            print("File not found.")
                            continue
                    else:
                        print("File not found.")
                        continue
                push_state("style-import")
                apply_style_config(fname)
            except Exception as e:
                print(f"Error importing style: {e}")
        elif key == 'e':
            try:
                filename = input("Enter filename (default SVG if no extension, q=cancel): ").strip()
                if not filename or filename.lower() == 'q':
                    print("Canceled.")
                else:
                    if not os.path.splitext(filename)[1]:
                        filename += ".svg"
                    # Confirm overwrite if file exists
                    export_target = _confirm_overwrite(filename)
                    if not export_target:
                        print("Export canceled.")
                    else:
                        # Temporarily remove numbering for export
                        for i, txt in enumerate(label_text_objects):
                            txt.set_text(labels[i])
                        fig.savefig(export_target, dpi=300)
                        print(f"Figure saved to {export_target}")
                        for i, txt in enumerate(label_text_objects):
                            txt.set_text(f"{i+1}: {labels[i]}")
                        fig.canvas.draw()
            except Exception as e:
                print(f"Error saving figure: {e}")
        # (Add delta 'd' branch here if present; ensure push_state at start)
        elif key == 'v':
            try:
                rng_in = input("Peak X range (min max, 'current' for axes limits, q=cancel): ").strip().lower()
                if not rng_in or rng_in == 'q':
                    print("Canceled.")
                    continue
                if rng_in == 'current':
                    x_min, x_max = ax.get_xlim()
                else:
                    parts = rng_in.split()
                    if len(parts) != 2:
                        print("Need exactly two numbers or 'current'.")
                        continue
                    x_min, x_max = map(float, parts)
                    if x_min > x_max:
                        x_min, x_max = x_max, x_min

                frac_in = input("Min relative peak height (0–1, default 0.1): ").strip()
                min_frac = float(frac_in) if frac_in else 0.1
                if min_frac < 0: min_frac = 0.0
                if min_frac > 1: min_frac = 1.0

                swin = input("Smoothing window (odd int >=3, blank=none): ").strip()
                if swin:
                    try:
                        win = int(swin)
                        if win < 3 or win % 2 == 0:
                            print("Invalid window; disabling smoothing.")
                            win = 0
                        else:
                            print(f"Using moving-average smoothing (window={win}).")
                    except ValueError:
                        print("Bad window value; no smoothing.")
                        win = 0
                else:
                    win = 0

                print("\n--- Peak Report ---")
                print(f"X range used: {x_min} .. {x_max}  (relative height threshold={min_frac})")
                for i, (x_arr, y_off) in enumerate(zip(x_data_list, y_data_list)):
                    # Recover original curve (remove vertical offset)
                    if i < len(offsets_list):
                        y_arr = y_off - offsets_list[i]
                    else:
                        y_arr = y_off.copy()

                    # Restrict to selected window
                    mask = (x_arr >= x_min) & (x_arr <= x_max)
                    x_sel = x_arr[mask]
                    y_sel = y_arr[mask]

                    label = labels[i] if i < len(labels) else f"Curve {i+1}"
                    print(f"\nCurve {i+1}: {label}")
                    if x_sel.size < 3:
                        print("  (Insufficient points)")
                        continue

                    # Optional smoothing
                    if win >= 3 and x_sel.size >= win:
                        kernel = np.ones(win, dtype=float) / win
                        y_sm = np.convolve(y_sel, kernel, mode='same')
                    else:
                        y_sm = y_sel

                    # Determine threshold
                    ymax = float(np.max(y_sm))
                    if ymax <= 0:
                        print("  (Non-positive data)")
                        continue
                    min_height = ymax * min_frac

                    # Simple local maxima detection
                    y_prev = y_sm[:-2]
                    y_mid  = y_sm[1:-1]
                    y_next = y_sm[2:]
                    core_mask = (y_mid > y_prev) & (y_mid >= y_next) & (y_mid >= min_height)
                    if not np.any(core_mask):
                        print("  (No peaks)")
                        continue
                    peak_indices = np.where(core_mask)[0] + 1  # shift because we looked at 1..n-2

                    # Optional refine: keep only distinct peaks (skip adjacent equal plateau)
                    peaks = []
                    last_idx = -10
                    for pi in peak_indices:
                        if pi - last_idx == 1 and y_sm[pi] == y_sm[last_idx]:
                            # same plateau, keep first
                            continue
                        peaks.append(pi)
                        last_idx = pi

                    print("  Peaks (x, y):")
                    for pi in peaks:
                        print(f"    x={x_sel[pi]:.6g}, y={y_sel[pi]:.6g}")
                print("\n--- End Peak Report ---\n")
            except Exception as e:
                print(f"Error finding peaks: {e}")
#
# ---------------- Argument Parsing ----------------
parser = argparse.ArgumentParser(
    description="batplot: Plot diffraction / PDF / XAS data (.xye, .xy, .qye, .dat, .csv, .gr, .nor, .chik, .chir, .txt)\n"
                "  --delta or -d : vertical offset between curves (default 0.0 if --stack)\n"
                "  --xrange min max : X-axis range (2θ or Q), Example: --xrange 2 10\n"
                "  --out or -o : output image filename (default SVG), Example: --out figure.svg\n"
                "  --xaxis : X-axis type override if the file extension is not recognized (choose from: 2theta, Q, r, k, energy, rft, or 'user defined')\n"
                "  --wl : global wavelength (Å) for Q conversion, Example: --wl 1.5406\n"
                "  --fullprof : FullProf matrix: xstart xend xstep [wavelength], Example: --fullprof 2 10 0.02 1.5406\n"
                "  --raw : plot raw intensity values instead of normalized\n"
                "  --stack : stack curves from top to bottom\n"
                "  --interactive : keep figure open for interactive editing\n\n"
                "File type and X-axis selection:\n"
                "  - .qye: X axis is Q\n"
                "  - .gr: X axis is r\n"
                "  - .nor: X axis is Energy (eV)\n"
                "  - .chik: X axis is k\n"
                "  - .chir: X axis is r\n"
                "  - .txt: Treated as generic 2-column data.\n"
                "  If none of the files have a recognized extension, you must either provide a wavelength to each file (if you want to plot everything in Q space) or specify --xaxis (Q, 2theta, r, k, energy, rft, or 'user defined').\n\n"
                "Example usages:\n"
                "  batplot file1.xye:1.5406 file2.qye --stack --interactive\n"
                "  batplot file1.dat file2.dat --wl 1.5406 --delta 1.0 --out figure.svg\n"
                "  batplot file1.dat file2.xy --xaxis 2theta --raw --xrange 2 10\n"
                "  batplot file1.qye file2.xye:1.54 structure1.cif structure2.cif --stack --interactive\n\n"
                "Extra usage:\n"
                "  batplot FOLDER    -> batch export all supported files in FOLDER to FOLDER/batplot_svg/*.svg\n"
                "  batplot all       -> batch export all supported files in current directory to ./batplot_svg/*.svg\n",
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("files", nargs="*", help=argparse.SUPPRESS)
parser.add_argument("--delta", "-d", type=float, default=None, help=argparse.SUPPRESS)
parser.add_argument("--autoscale", action="store_true", help=argparse.SUPPRESS)
parser.add_argument("--xrange", "-r", nargs=2, type=float, help=argparse.SUPPRESS)
parser.add_argument("--out", "-o", type=str, help=argparse.SUPPRESS)
parser.add_argument("--errors", action="store_true", help=argparse.SUPPRESS)
parser.add_argument("--xaxis", type=str, help=argparse.SUPPRESS)
parser.add_argument("--convert", "-c", nargs="+", help=argparse.SUPPRESS)
parser.add_argument("--wl", type=float, help=argparse.SUPPRESS)
parser.add_argument("--fullprof", nargs="+", type=float, help=argparse.SUPPRESS)
parser.add_argument("--raw", action="store_true", help=argparse.SUPPRESS)
parser.add_argument("--interactive", action="store_true", help=argparse.SUPPRESS)
parser.add_argument("--savefig", type=str, help=argparse.SUPPRESS)
parser.add_argument("--stack", action="store_true", help=argparse.SUPPRESS)

# parser.add_argument("files", nargs="*", help="Files to plot. Optionally specify wavelength per file: file.xye")
# parser.add_argument("--delta", "-d", type=float, default=None,
#                     help="Vertical offset between curves (default 0.0 if --stack). Example: --delta 0.2")#parser.add_argument("--autoscale", action="store_true", help="Scale offsets relative to max intensity per curve")
# parser.add_argument("--xrange", nargs=2, type=float, help="X-axis range: min max (2θ or Q), Example: --xrange 2 10")
# parser.add_argument("--out", "-o", type=str, help="Output image filename (default SVG), Example: --out figure.svg")
# parser.add_argument("--errors", action="store_true", help="Plot error bars if present")
# parser.add_argument("--xaxis", choices=["2theta", "Q", "r"],
#                     help="X-axis type override (2theta, Q, or r for PDF)")
# parser.add_argument("--convert", "-c", nargs="+", help="Convert .xye/.dat files to .qye using --wl")
# parser.add_argument("--wl", type=float, help="Global wavelength (Å) for Q conversion, Example: --wl 1.5406 (alternatively specify per file with ':', Example: file.xye:1.5406)")
# parser.add_argument("--fullprof", nargs="+", type=float, help="FullProf matrix: xstart xend xstep [wavelength], Example: --fullprof 2 10 0.02 1.5406")
# parser.add_argument("--raw", action="store_true", help="Plot raw intensity values instead of normalized")
# parser.add_argument("--savefig", type=str, help="Save figure object for later editing (.pkl)")
# parser.add_argument("--stack", action="store_true",
#                     help="Stack curves from top to bottom")
# parser.add_argument("--interactive", action="store_true", help="Keep figure open for interactive editing\n")
# parser.add_argument("Example usages:")
# parser.add_argument("batplot file1.xye file2.qye:1.5406 --stack --interactive")
# parser.add_argument("batplot file1.dat --xaxis Q --wl 1.5406 --delta 0.1 --out figure.svg")
# parser.add_argument("batplot file1.xy file2.xy --raw --xrange 2 10")
# parser.add_argument("batplot file1.qye file2.xye:1.54 structure1.cif structure2.cif --stack --interactive")
# parser.add_argument("batplot all")

args = parser.parse_args()

# ---------------- Batch Processing (directory or 'all') ----------------
def batch_process(directory: str, args):
    print(f"Batch mode: scanning {directory}")
    supported_ext = {'.xye', '.xy', '.qye', '.dat', '.csv', '.gr', '.nor', '.chik', '.chir', '.txt'}  # added .xy, .txt
    out_dir = os.path.join(directory, "batplot_svg")
    os.makedirs(out_dir, exist_ok=True)
    files = [f for f in sorted(os.listdir(directory))
             if os.path.splitext(f)[1].lower() in supported_ext and os.path.isfile(os.path.join(directory, f))]
    if not files:
        print("No supported data files found.")
        return
    print(f"Found {len(files)} supported files. Exporting SVG plots to {out_dir}")
    for fname in files:
        fpath = os.path.join(directory, fname)
        ext = os.path.splitext(fname)[1].lower()
        try:
            # ---- Read data ----
            if ext == '.gr':
                x, y = read_gr_file(fpath); e = None
                axis_mode = 'r'
            elif ext == '.nor':
                data = np.loadtxt(fpath, comments="#")
                if data.ndim == 1: data = data.reshape(1, -1)
                if data.shape[1] < 2: raise ValueError("Invalid .nor format")
                x, y = data[:,0], data[:,1]
                e = data[:,2] if data.shape[1] >= 3 else None
                axis_mode = 'energy'
                pass
            elif 'chik' in ext:
                data = np.loadtxt(fpath, comments="#")
                if data.ndim == 1: data = data.reshape(1, -1)
                if data.shape[1] < 2: raise ValueError("Invalid .chik data")
                x, y = data[:,0], data[:,1]; e = data[:,2] if data.shape[1] >= 3 else None
                axis_mode = 'k'
            elif 'chir' in ext:
                data = np.loadtxt(fpath, comments="#")
                if data.ndim == 1: data = data.reshape(1, -1)
                if data.shape[1] < 2: raise ValueError("Invalid .chir data")
                x, y = data[:,0], data[:,1]; e = data[:,2] if data.shape[1] >= 3 else None
                axis_mode = 'rft'
            else:
                # Support .txt as generic 2-column data
                data = np.loadtxt(fpath, comments="#")
                if data.ndim == 1: data = data.reshape(1, -1)
                if data.shape[1] < 2: raise ValueError("Invalid 2-column data")
                x, y = data[:,0], data[:,1]
                e = data[:,2] if data.shape[1] >= 3 else None
                # Decide axis: priority: user --xaxis, .qye -> Q, .gr -> r, .nor -> energy, .chik -> k, .chir -> rft, else prompt for --xaxis
                if ext == '.qye':
                    axis_mode = 'Q'
                elif ext == '.gr':
                    axis_mode = 'r'
                elif ext == '.nor':
                    axis_mode = 'energy'
                elif 'chik' in ext:
                    axis_mode = 'k'
                elif 'chir' in ext:
                    axis_mode = 'rft'
                elif args.xaxis:
                    axis_mode = args.xaxis
                else:
                    raise ValueError("Cannot determine X-axis type for file {} (need .qye / .gr / .nor / .chik / .chir or specify --xaxis).".format(fname))
            # ---- Convert to Q if needed ----
            if axis_mode == 'Q' and ext not in ('.qye', '.gr', '.nor'):
                if args.wl is None:
                    # Cannot convert without wavelength
                    axis_mode = '2theta'  # fallback
                else:
                    theta_rad = np.radians(x/2)
                    x_plot = 4*np.pi*np.sin(theta_rad)/args.wl
            else:
                x_plot = x
            # ---- Normalize or raw ----
            if args.raw:
                y_plot = y.copy()
            else:
                if y.size:
                    ymin = float(y.min()); ymax = float(y.max())
                    span = ymax - ymin
                    y_plot = (y - ymin)/span if span > 0 else np.zeros_like(y)
                else:
                    y_plot = y
            # ---- Plot single figure ----
            fig_b, ax_b = plt.subplots(figsize=(6,4))
            ax_b.plot(x_plot, y_plot, lw=1)
            if axis_mode == 'Q':
                ax_b.set_xlabel(r"Q ($\mathrm{\AA}^{-1}$)")
            elif axis_mode == 'r':
                ax_b.set_xlabel("r (Å)")
            elif axis_mode == 'energy':
                ax_b.set_xlabel("Energy (eV)")
            elif axis_mode == 'k':
                ax_b.set_xlabel(r"k ($\mathrm{\AA}^{-1}$)")
            elif axis_mode == 'rft':
                ax_b.set_xlabel("Radial distance (Å)")
            else:
                ax_b.set_xlabel(r"$2\theta\ (\mathrm{deg})$")
            ax_b.set_ylabel("Intensity" if args.raw else "Normalized intensity (a.u.)")
            ax_b.set_title(fname)
            fig_b.subplots_adjust(left=0.18, right=0.97, bottom=0.16, top=0.90)
            out_name = os.path.splitext(fname)[0] + ".svg"
            out_path = os.path.join(out_dir, out_name)
            target = _confirm_overwrite(out_path)
            if not target:
                plt.close(fig_b)
                print(f"  Skipped {out_name} (user canceled)")
            else:
                fig_b.savefig(target, dpi=300)
                plt.close(fig_b)
                print(f"  Saved {os.path.basename(target)}")
        except Exception as e:
            print(f"  Skipped {fname}: {e}")
    print("Batch processing complete.")

# Detect batch invocation: exactly one positional argument and it's a dir OR 'all'
if len(args.files) == 1:
    sole = args.files[0]
    if sole.lower() == 'all':
        batch_process(os.getcwd(), args)
        exit()
    elif os.path.isdir(sole):
        batch_process(os.path.abspath(sole), args)
        exit()

# ---------------- Normal (multi-file) path continues below ----------------
# Apply conditional default for delta (normal mode only)
if args.delta is None:
    args.delta = 0.1 if args.stack else 0.0

# ---------------- Automatic session (.pkl) load shortcut ----------------
# If user invokes: batplot session.pkl [--interactive]
if len(args.files) == 1 and args.files[0].lower().endswith('.pkl'):
    sess_path = args.files[0]
    if not os.path.isfile(sess_path):
        print(f"Session file not found: {sess_path}")
        exit(1)
    try:
        with open(sess_path, 'rb') as f:
            sess = pickle.load(f)
        if not isinstance(sess, dict) or 'version' not in sess:
            print("Not a valid batplot session file.")
            exit(1)
    except Exception as e:
        print(f"Failed to load session: {e}")
        exit(1)
    # Reconstruct minimal state and go to interactive if requested
    plt.ion() if args.interactive else None
    fig, ax = plt.subplots(figsize=(8,6))
    y_data_list = []
    x_data_list = []
    labels_list = []
    orig_y = []
    label_text_objects = []
    x_full_list = []
    raw_y_full_list = []
    offsets_list = []
    tick_state = {
        'bx': True,'tx': False,'ly': True,'ry': False,
        'mbx': False,'mtx': False,'mly': False,'mry': False
    }
    saved_stack = bool(sess.get('args_subset', {}).get('stack', False))
    # Pull data
    # --- Robust reconstruction of stored curves ---
    x_loaded = sess.get('x_data', [])
    y_loaded = sess.get('y_data', [])  # stored plotted (baseline+offset) values
    orig_loaded = sess.get('orig_y', [])  # stored baseline (normalized/raw w/out offsets)
    offsets_saved = sess.get('offsets', [])
    n_curves = len(x_loaded)
    for i in range(n_curves):
        x_arr = np.array(x_loaded[i])
        off = offsets_saved[i] if i < len(offsets_saved) else 0.0
        if orig_loaded and i < len(orig_loaded):
            base = np.array(orig_loaded[i])
        else:
            # Fallback: derive baseline by subtracting offset from stored y (handles legacy sessions)
            y_arr_full = np.array(y_loaded[i]) if i < len(y_loaded) else np.array([])
            base = y_arr_full - off
        y_plot = base + off
        x_data_list.append(x_arr)
        orig_y.append(base)
        y_data_list.append(y_plot)
        ax.plot(x_arr, y_plot, lw=1)
        x_full_list.append(x_arr.copy())
        raw_y_full_list.append(base.copy())
    offsets_list[:] = offsets_saved if offsets_saved else [0.0]*n_curves
    # Apply stored line styles (if any)
    try:
        stored_styles = sess.get('line_styles', [])
        for ln, st in zip(ax.lines, stored_styles):
            if 'color' in st: ln.set_color(st['color'])
            if 'linewidth' in st: ln.set_linewidth(st['linewidth'])
            if 'linestyle' in st:
                try: ln.set_linestyle(st['linestyle'])
                except Exception: pass
            if 'alpha' in st and st['alpha'] is not None: ln.set_alpha(st['alpha'])
            if 'marker' in st and st['marker'] is not None:
                try: ln.set_marker(st['marker'])
                except Exception: pass
            if 'markersize' in st and st['markersize'] is not None:
                try: ln.set_markersize(st['markersize'])
                except Exception: pass
            if 'markerfacecolor' in st and st['markerfacecolor'] is not None:
                try: ln.set_markerfacecolor(st['markerfacecolor'])
                except Exception: pass
            if 'markeredgecolor' in st and st['markeredgecolor'] is not None:
                try: ln.set_markeredgecolor(st['markeredgecolor'])
                except Exception: pass
    except Exception:
        pass
    labels_list[:] = sess.get('labels', [f"Curve {i+1}" for i in range(len(y_data_list))])
    delta = sess.get('delta', 0.0)
    ax.set_xlabel(sess.get('axis', {}).get('xlabel', 'X'))
    ax.set_ylabel(sess.get('axis', {}).get('ylabel', 'Intensity'))
    if 'xlim' in sess.get('axis', {}):
        ax.set_xlim(*sess['axis']['xlim'])
    if 'ylim' in sess.get('axis', {}):
        ax.set_ylim(*sess['axis']['ylim'])
    # Apply figure size & dpi if stored
    fig_cfg = sess.get('figure', {})
    try:
        if fig_cfg.get('size') and isinstance(fig_cfg['size'], (list, tuple)) and len(fig_cfg['size']) == 2:
            fw, fh = fig_cfg['size']
            if not globals().get('keep_canvas_fixed', True):
                fig.set_size_inches(float(fw), float(fh), forward=True)
            else:
                print("(Canvas fixed) Ignoring session figure size restore.")
        if 'dpi' in fig_cfg:
            try: fig.set_dpi(int(fig_cfg['dpi']))
            except Exception: pass
    except Exception:
        pass
    # Font
    font_cfg = sess.get('font', {})
    if font_cfg.get('chain'):
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = font_cfg['chain']
    if font_cfg.get('size'):
        plt.rcParams['font.size'] = font_cfg['size']
    # Tick state restore
    saved_tick = sess.get('tick_state', {})
    for k,v in saved_tick.items():
        if k in tick_state: tick_state[k] = v
    # Rebuild label texts
    for i, lab in enumerate(labels_list):
        txt = ax.text(1.0, 1.0, f"{i+1}: {lab}", ha='right', va='top', transform=ax.transAxes,
                      fontsize=plt.rcParams.get('font.size', 12))
        label_text_objects.append(txt)
    # CIF tick series (optional)
    cif_tick_series = sess.get('cif_tick_series') or []
    cif_hkl_map = {k: [tuple(v) for v in val] for k,val in sess.get('cif_hkl_map', {}).items()}
    cif_hkl_label_map = {k: dict(v) for k,v in sess.get('cif_hkl_label_map', {}).items()}
    cif_numbering_enabled = True
    cif_extend_suspended = False
    show_cif_hkl = sess.get('show_cif_hkl', False)
    # Provide minimal stubs to satisfy interactive menu dependencies
    # Axis mode restoration informs downstream toggles (e.g., CIF conversions, crosshair availability)
    axis_mode_restored = sess.get('axis_mode', 'unknown')
    use_Q = axis_mode_restored == 'Q'
    use_r = axis_mode_restored == 'r'
    use_E = axis_mode_restored == 'energy'
    use_k = axis_mode_restored == 'k'
    use_rft = axis_mode_restored == 'rft'
    use_2th = axis_mode_restored == '2theta'
    x_label = ax.get_xlabel() or 'X'
    def update_tick_visibility_local():
        ax.tick_params(axis='x', bottom=tick_state['bx'], top=tick_state['tx'], labelbottom=tick_state['bx'], labeltop=tick_state['tx'])
        ax.tick_params(axis='y', left=tick_state['ly'], right=tick_state['ry'], labelleft=tick_state['ly'], labelright=tick_state['ry'])
    update_tick_visibility_local()
    # Ensure label positions correct
    update_labels(ax, y_data_list, label_text_objects, saved_stack)
    if cif_tick_series:
        # Provide draw/extend helpers compatible with interactive menu using original placement logic
        def _session_cif_extend(xmax_domain):
            # Minimal extension: do nothing (could replicate original if needed)
            return
        def _session_cif_draw():
            if not cif_tick_series:
                return
            try:
                cur_ylim = ax.get_ylim(); yr = cur_ylim[1]-cur_ylim[0]
                if yr <= 0: yr = 1.0
                # Determine mixed vs CIF-only
                cif_only_local = (len(cif_tick_series) > 0 and len(ax.lines) == 0)
                if saved_stack or len(y_data_list) > 1:
                    global_min = min(float(a.min()) for a in y_data_list if len(a)) if y_data_list else cur_ylim[0]
                    base = global_min - 0.08*yr; spacing = 0.05*yr
                else:
                    global_min = min(float(a.min()) for a in y_data_list if len(a)) if y_data_list else 0.0
                    base = global_min - 0.06*yr; spacing = 0.04*yr
                needed_min = base - (len(cif_tick_series)-1)*spacing - 0.04*yr
                if needed_min < cur_ylim[0]:
                    ax.set_ylim(needed_min, cur_ylim[1]); cur_ylim = ax.get_ylim(); yr = cur_ylim[1]-cur_ylim[0]
                # Clear previous artifacts
                for art in getattr(ax, '_cif_tick_art', []):
                    try: art.remove()
                    except Exception: pass
                new_art = []
                show_hkl_local = bool(show_cif_hkl)
                # Draw each series
                for i,(lab,fname,peaksQ,wl,qmax_sim,color) in enumerate(cif_tick_series):
                    y_line = base - i*spacing
                    # Convert peaks based on axis mode if known (no wavelength conversion here if wl missing)
                    domain_peaks = peaksQ
                    # Clip to visible x-range
                    xlow,xhigh = ax.get_xlim()
                    domain_peaks = [p for p in domain_peaks if xlow <= p <= xhigh]
                    # Build hkl label map
                    label_map = cif_hkl_label_map.get(fname, {}) if show_hkl_local else {}
                    if show_hkl_local and len(domain_peaks) > 4000:
                        show_hkl_local = False  # safety
                    for p in domain_peaks:
                        ln, = ax.plot([p,p],[y_line, y_line+0.02*yr], color=color, lw=1.0, alpha=0.9, zorder=3)
                        new_art.append(ln)
                        if show_hkl_local:
                            lbl = label_map.get(round(p,6))
                            if lbl:
                                t_hkl = ax.text(p, y_line+0.022*yr, lbl, ha='center', va='bottom', fontsize=7, rotation=90, color=color)
                                new_art.append(t_hkl)
                    # Removed numbering prefix; keep one leading space for padding from axis
                    label_text = f" {lab}"
                    txt = ax.text(ax.get_xlim()[0], y_line+0.005*yr, label_text,
                                  ha='left', va='bottom', fontsize=max(8,int(0.55*plt.rcParams.get('font.size',12))), color=color)
                    new_art.append(txt)
                ax._cif_tick_art = new_art
                fig.canvas.draw_idle()
            except Exception:
                pass
        ax._cif_extend_func = _session_cif_extend
        ax._cif_draw_func = _session_cif_draw
        ax._cif_draw_func()
    if args.interactive:
        try:
            args.stack = saved_stack
        except Exception:
            pass
        interactive_menu(fig, ax, y_data_list, x_data_list, labels_list,
                         orig_y, label_text_objects, delta, x_label, args,
                         x_full_list, raw_y_full_list, offsets_list,
                         use_Q, use_r, use_E, use_k, use_rft)
    else:
        plt.show()
    exit()

# ---------------- Handle conversion ----------------
if args.convert:
    if args.wl is None:
        print("Error: --wl is required for --convert")
       
        exit(1)
    convert_to_qye(args.convert, args.wl)
    exit()

# ---------------- Plotting ----------------
offset = 0.0
direction = -1 if args.stack else 1  # stack downward
if args.interactive:
    plt.ion()
fig, ax = plt.subplots(figsize=(8, 6))

y_data_list = []
x_data_list = []
labels_list = []
orig_y = []
label_text_objects = []
# New lists to preserve full data & offsets
x_full_list = []
raw_y_full_list = []
offsets_list = []

# ---------------- Determine X-axis type ----------------
def _ext_token(path):
    return os.path.splitext(path)[1].lower()  # includes leading dot
any_qye = any(f.lower().endswith(".qye") for f in args.files)
any_gr  = any(f.lower().endswith(".gr")  for f in args.files)
any_nor = any(f.lower().endswith(".nor") for f in args.files)
any_chik = any("chik" in _ext_token(f) for f in args.files)
any_chir = any("chir" in _ext_token(f) for f in args.files)
any_txt = any(f.lower().endswith(".txt") for f in args.files)
any_cif = any(f.lower().endswith(".cif") for f in args.files)
non_cif_count = sum(0 if f.lower().endswith('.cif') else 1 for f in args.files)
cif_only = any_cif and non_cif_count == 0
any_lambda = any(":" in f for f in args.files) or args.wl is not None

# Incompatibilities (no mixing of fundamentally different axis domains)
if sum(bool(x) for x in (any_gr, any_nor, any_chik, any_chir, (any_qye or any_lambda or any_cif))) > 1:
    raise ValueError("Cannot mix .gr (r), .nor (energy), .chik (k), .chir (FT-EXAFS R), and Q/2θ/CIF data together. Split runs.")

# Automatic axis selection based on file extensions
if any_qye:
    axis_mode = "Q"
elif any_gr:
    axis_mode = "r"
elif any_nor:
    axis_mode = "energy"
elif any_chik:
    axis_mode = "k"
elif any_chir:
    axis_mode = "rft"
elif any_txt:
    # .txt is generic, require --xaxis
    if args.xaxis:
        axis_mode = args.xaxis
    else:
        raise ValueError("Cannot determine X-axis type for .txt files. Please specify --xaxis (Q, 2theta, r, k, energy, rft, or 'user defined').")
elif any_qye or any_lambda or any_cif:
    if args.xaxis and args.xaxis.lower() in ("2theta","two_theta","tth"):
        axis_mode = "2theta"
    else:
        axis_mode = "Q"
elif args.xaxis:
    axis_mode = args.xaxis
else:
    raise ValueError("Cannot determine X-axis type (need .qye / .gr / .nor / .chik / .chir / .cif / wavelength / --xaxis). For .txt or unknown file types, use --xaxis Q, 2theta, r, k, energy, rft, or 'user defined'.")

use_Q   = axis_mode == "Q"
use_2th = axis_mode == "2theta"
use_r   = axis_mode == "r"
use_E   = axis_mode == "energy"
use_k   = axis_mode == "k"      # NEW
use_rft = axis_mode == "rft"    # NEW

# ---------------- Read and plot files ----------------
# Helper to extract discrete peak positions from a simulated CIF pattern by local maxima picking
def _extract_peak_positions(Q_array, I_array, min_rel_height=0.05):
    if Q_array.size == 0 or I_array.size == 0:
        return []
    Imax = I_array.max() if I_array.size else 0
    if Imax <= 0:
        return []
    thr = Imax * min_rel_height
    peaks = []
    for i in range(1, len(I_array)-1):
        if I_array[i] >= thr and I_array[i] >= I_array[i-1] and I_array[i] >= I_array[i+1]:
            # simple peak refine by local quadratic (optional)
            y1,y2,y3 = I_array[i-1], I_array[i], I_array[i+1]
            x1,x2,x3 = Q_array[i-1], Q_array[i], Q_array[i+1]
            denom = (y1 - 2*y2 + y3)
            if abs(denom) > 1e-12:
                dx = 0.5*(y1 - y3)/denom
                if -0.6 < dx < 0.6:
                    xc = x2 + dx*(x3 - x1)/2.0
                    if Q_array[0] <= xc <= Q_array[-1]:
                        peaks.append(xc)
                        continue
            peaks.append(Q_array[i])
    return peaks

# Will accumulate CIF tick series to render after main curves
cif_tick_series = []  # list of (label, filename, peak_positions_Q, wavelength_or_None, qmax_simulated, color)
cif_hkl_map = {}      # filename -> list of (Q,h,k,l)
cif_hkl_label_map = {}  # filename -> dict of Q -> label string
cif_numbering_enabled = True  # show numbering for CIF tick sets (mixed mode only)
cif_extend_suspended = False  # guard flag to prevent auto extension during certain operations
QUIET_CIF_EXTEND = True  # suppress extension debug output

# Cached wavelength for CIF tick conversion (prevents interactive blocking prompts)
cif_cached_wavelength = None
show_cif_hkl = False

for idx_file, file_entry in enumerate(args.files):
    parts = file_entry.split(":")
    fname = parts[0]
    wavelength_file = float(parts[-1]) if len(parts) > 1 else args.wl
    if not os.path.isfile(fname):
        print(f"File not found: {fname}")
        continue
    file_ext = os.path.splitext(fname)[1].lower()
    is_chik = "chik" in file_ext
    is_chir = "chir" in file_ext
    is_cif  = file_ext == '.cif'
    label = os.path.basename(fname)
    if wavelength_file and not use_r and not use_E and file_ext not in (".gr", ".nor", ".cif"):
        label += f" (λ={wavelength_file:.5f} Å)"

    # ---- Read data (added .nor branch) ----
    if is_cif:
        try:
            # Simulate pattern directly in Q space regardless of current axis_mode
            Q_sim, I_sim = simulate_cif_pattern_Q(fname)
            x = Q_sim
            y = I_sim
            e = None
            # Force axis mode if needed
            if not (use_Q or use_2th):
                use_Q = True
            # Full reflection list (no wavelength filtering in pure Q domain)
            refl = cif_reflection_positions(fname, Qmax=float(Q_sim[-1]) if len(Q_sim) else 0.0, wavelength=None)
            # default tick color black
            cif_tick_series.append((label, fname, refl, None, float(Q_sim[-1]) if len(Q_sim) else 0.0, 'k'))
            # If CIF mixed with other data types, do NOT plot intensity curve (ticks only)
            if not cif_only:
                continue  # skip rest of loop so curve isn't added
        except Exception as e_read:
            print(f"Error simulating CIF {fname}: {e_read}")
            continue
    elif file_ext == ".gr":
        try:
            x, y = read_gr_file(fname); e = None
        except Exception as e_read:
            print(f"Error reading {fname}: {e_read}"); continue
    elif file_ext in [".nor", ".xy", ".xye", ".qye", ".dat", ".csv"] or is_chik or is_chir:
        # Robustly skip header/comment/non-numeric lines until data is found
        def robust_loadtxt_skipheader(fname):
            data_lines = []
            with open(fname, "r") as f:
                for line in f:
                    ls = line.strip()
                    if not ls or ls.startswith("#"): continue
                    # Try to parse at least 2 floats
                    floats = []
                    for p in ls.replace(",", " ").split():
                        try:
                            floats.append(float(p))
                        except ValueError:
                            break
                    if len(floats) >= 2:
                        data_lines.append(ls)
            if not data_lines:
                raise ValueError(f"No numeric data found in {fname}")
            from io import StringIO
            return np.loadtxt(StringIO("\n".join(data_lines)))

        try:
            data = robust_loadtxt_skipheader(fname)
        except Exception as e_read:
            print(f"Error reading {fname}: {e_read}"); continue
        if data.ndim == 1: data = data.reshape(1, -1)
        if data.shape[1] < 2:
            print(f"Invalid data format in {fname}"); continue
        x, y = data[:, 0], data[:, 1]
        e = data[:, 2] if data.shape[1] >= 3 else None
        # For .csv, .dat, .xy, .xye, .qye, .nor, .chik, .chir, this robustly skips headers
    elif args.fullprof and file_ext == ".dat":
        try:
            y_plot, n_rows = read_fullprof_rowwise(fname)
            xstart, xend, xstep = args.fullprof[0], args.fullprof[1], args.fullprof[2]
            x_plot = np.linspace(xstart, xend, len(y_plot))
            wavelength = args.fullprof[3] if len(args.fullprof)>=4 else wavelength_file
            if use_Q and wavelength:
                theta_rad = np.radians(x_plot / 2)
                x_plot = 4*np.pi*np.sin(theta_rad)/wavelength
            e_plot = None
        except Exception as e:
            print(f"Error reading FullProf-style {fname}: {e}")
            continue

    # ---- X-axis conversion logic updated (no conversion for energy) ----
    if use_Q and file_ext not in (".qye", ".gr", ".nor"):
        if wavelength_file:
            theta_rad = np.radians(x/2)
            x_plot = 4*np.pi*np.sin(theta_rad)/wavelength_file
        else:
            x_plot = x
    else:
        # r, energy, or already Q: direct
        x_plot = x

    # ---- Store full (converted) arrays BEFORE cropping ----
    x_full = x_plot.copy()
    y_full_raw = y.copy()
    raw_y_full_list.append(y_full_raw)
    x_full_list.append(x_full)

    # ---- Apply xrange (for initial display only; full data kept above) ----
    y_plot = y_full_raw
    e_plot = e
    if args.xrange:
        mask = (x_full>=args.xrange[0]) & (x_full<=args.xrange[1])
        ax.set_xlim(args.xrange[0], args.xrange[1])
        x_plot = x_full[mask]
        y_plot = y_full_raw[mask]
        if e_plot is not None:
            e_plot = e_plot[mask]
    else:
        x_plot = x_full

    # ---- Normalize (display subset) ----
    if not args.raw:
        # Min–max normalization to 0..1 within the currently displayed (cropped) segment
        if y_plot.size:
            y_min = float(y_plot.min())
            y_max = float(y_plot.max())
            span = y_max - y_min
            if span > 0:
                y_norm = (y_plot - y_min) / span
            else:
                # Flat line -> all zeros
                y_norm = np.zeros_like(y_plot)
        else:
            y_norm = y_plot
    else:
        y_norm = y_plot

    # ---- Apply offset (waterfall vs stack) ----
    if args.stack:
        y_plot_offset = y_norm + offset
        y_range = (y_norm.max() - y_norm.min()) if y_norm.size else 0.0
        gap = y_range + (args.delta * (y_range if args.autoscale else 1.0))
        offsets_list.append(offset)
        offset -= gap
    else:
        increment = (y_norm.max() - y_norm.min()) * args.delta if (args.autoscale and y_norm.size) else args.delta
        y_plot_offset = y_norm + offset
        offsets_list.append(offset)
        offset += increment

    # ---- Plot curve ----
    ax.plot(x_plot, y_plot_offset, "-", lw=1, alpha=0.8)
    y_data_list.append(y_plot_offset.copy())
    x_data_list.append(x_plot)
    labels_list.append(label)
    # Store current normalized (subset) (used by rearrange logic)
    orig_y.append(y_norm.copy())

# ---------------- Force axis to fit all data before labels ----------------
ax.relim()
ax.autoscale_view()
fig.canvas.draw()

# Define a sample_tick safely (may be None if no labels yet)
sample_tick = None
xt_lbls = ax.get_xticklabels()
if xt_lbls:
    sample_tick = xt_lbls[0]

else:
    yt_lbls = ax.get_yticklabels()
    if yt_lbls:
        sample_tick = yt_lbls[0]

# ---------------- Initial label creation (REPLACED BLOCK) ----------------
# Remove the old simple per-curve placement loop and use:
label_text_objects = []
tick_fs = sample_tick.get_fontsize() if sample_tick else plt.rcParams.get('font.size', 12)
# get_fontname() may not exist on some backends; use family from rcParams if missing
try:
    tick_fn = sample_tick.get_fontname() if sample_tick else plt.rcParams.get('font.sans-serif', ['DejaVu Sans'])[0]
except Exception:
    tick_fn = plt.rcParams.get('font.sans-serif', ['DejaVu Sans'])[0]

if args.stack:
    x_max = ax.get_xlim()[1]
    for i, y_plot_offset in enumerate(y_data_list):
        y_max_curve = y_plot_offset.max() if len(y_plot_offset) else ax.get_ylim()[1]
        txt = ax.text(x_max, y_max_curve,
                      f"{i+1}: {labels_list[i]}",
                      va='top', ha='right',
                      fontsize=tick_fs, fontname=tick_fn,
                      transform=ax.transData)
        label_text_objects.append(txt)
else:
    n = len(y_data_list)
    top_pad = 0.02
    start_y = 0.98
    spacing = min(0.08, max(0.025, 0.90 / max(n, 1)))
    for i in range(n):
        y_pos = start_y - i * spacing
        if y_pos < 0.02:
            y_pos = 0.02
        txt = ax.text(1.0, y_pos,
                      f"{i+1}: {labels_list[i]}",
                      va='top', ha='right',
                      fontsize=tick_fs, fontname=tick_fn,
                      transform=ax.transAxes)
        label_text_objects.append(txt)

# Ensure consistent initial placement (especially for stacked mode)
update_labels(ax, y_data_list, label_text_objects, args.stack)

# ---------------- CIF tick overlay (after labels placed) ----------------
def _ensure_wavelength_for_2theta():
    """Ensure wavelength assigned to all CIF tick sets without prompting.

    Order of preference:
      1. Existing wavelength already stored in any series.
      2. args.wl if provided by user.
      3. Previously cached value (cif_cached_wavelength).
      4. Default 1.5406 Å.
    """
    global cif_cached_wavelength
    if not cif_tick_series:
        return None
    # If any entry already has wavelength, use and cache it
    for _lab,_fname,_peaks,_wl,_qmax,_color in cif_tick_series:
        if _wl is not None:
            cif_cached_wavelength = _wl
            return _wl
    wl = getattr(args, 'wl', None)
    if wl is None:
        wl = cif_cached_wavelength if cif_cached_wavelength is not None else 1.5406
    cif_cached_wavelength = wl
    for i,(lab, fname, peaksQ, w0, qmax_sim, color) in enumerate(cif_tick_series):
        cif_tick_series[i] = (lab, fname, peaksQ, wl, qmax_sim, color)
    return wl

def _Q_to_2theta(peaksQ, wl):
    out = []
    if wl is None:
        return out
    for q in peaksQ:
        s = q*wl/(4*np.pi)
        if 0 <= s < 1:
            out.append(np.degrees(2*np.arcsin(s)))
    return out

def extend_cif_tick_series(xmax_domain):
    """Extend CIF peak list if x-range upper bound increases beyond simulated Qmax.
    xmax_domain: upper x limit in current axis units (Q or 2θ).
    """
    if globals().get('cif_extend_suspended', False):
        return
    if not cif_tick_series:
        return
    # Determine target Q for extension depending on axis
    wl_any = None
    if use_2th:
        # Ensure wavelength known
        for _,_,_,wl_,_ in cif_tick_series:
            if wl_ is not None:
                wl_any = wl_
                break
        if wl_any is None:
            wl_any = _ensure_wavelength_for_2theta()
    updated = False
    for i,(lab,fname,peaksQ,wl,qmax_sim,color) in enumerate(cif_tick_series):
        if use_2th:
            wl_use = wl if wl is not None else wl_any
            theta_rad = np.radians(min(xmax_domain, 179.9)/2.0)
            Q_target = 4*np.pi*np.sin(theta_rad)/wl_use if wl_use else qmax_sim
        else:
            Q_target = xmax_domain
        if not QUIET_CIF_EXTEND:
            try:
                print(f"[CIF extend check] {lab}: current Qmax={qmax_sim:.3f}, target Q={Q_target:.3f}")
            except Exception:
                pass
        if Q_target > qmax_sim + 1e-6:
            new_Qmax = Q_target + 0.25
            try:
                # Only apply wavelength constraint for 2θ axis; in Q axis enumerate freely
                refl = cif_reflection_positions(fname, Qmax=new_Qmax, wavelength=(wl if (wl and use_2th) else None))
                cif_tick_series[i] = (lab, fname, refl, wl, float(new_Qmax), color)
                if not QUIET_CIF_EXTEND:
                    print(f"Extended CIF ticks for {lab} to Qmax={new_Qmax:.2f} (count={len(refl)})")
                updated = True
            except Exception as e:
                print(f"Warning: could not extend CIF peaks for {lab}: {e}")
    if updated:
        # After update, redraw ticks
        draw_cif_ticks()

def draw_cif_ticks():
    if not cif_tick_series:
        return
    cur_ylim = ax.get_ylim(); yr = cur_ylim[1]-cur_ylim[0]
    if yr <= 0: yr = 1.0
    if args.stack or len(y_data_list) > 1:
        global_min = min(float(a.min()) for a in y_data_list if len(a)) if y_data_list else cur_ylim[0]
        base = global_min - 0.08*yr; spacing = 0.05*yr
    else:
        global_min = min(float(a.min()) for a in y_data_list if len(a)) if y_data_list else 0.0
        base = global_min - 0.06*yr; spacing = 0.04*yr
    needed_min = base - (len(cif_tick_series)-1)*spacing - 0.04*yr
    if needed_min < cur_ylim[0]:
        ax.set_ylim(needed_min, cur_ylim[1]); cur_ylim = ax.get_ylim(); yr = cur_ylim[1]-cur_ylim[0]
    # Clear previous
    for art in getattr(ax, '_cif_tick_art', []):
        try: art.remove()
        except Exception: pass
    new_art = []
    mixed_mode = (not cif_only)  # cif_only variable defined earlier in script context
    show_hkl = globals().get('show_cif_hkl', False)
    for i,(lab, fname, peaksQ, wl, qmax_sim, color) in enumerate(cif_tick_series):
        y_line = base - i*spacing
        if use_2th:
            if wl is None: wl = _ensure_wavelength_for_2theta()
            domain_peaks = _Q_to_2theta(peaksQ, wl)
        else:
            domain_peaks = peaksQ
        # --- NEW: restrict to current visible x-range for performance ---
        xlow, xhigh = ax.get_xlim()
        if domain_peaks:
            # domain_peaks may be numpy array or list; create filtered list
            domain_peaks = [p for p in domain_peaks if xlow <= p <= xhigh]
        if not domain_peaks:
            # No peaks in current window; still write label row and continue
            # Removed numbering; keep space padding
            label_text = f" {lab}"
            txt = ax.text(ax.get_xlim()[0], y_line + 0.005*yr, label_text,
                          ha='left', va='bottom', fontsize=max(8,int(0.55*plt.rcParams.get('font.size',12))), color=color)
            new_art.append(txt)
            continue
        # Build map for quick hkl lookup by Q
        hkl_entries = cif_hkl_map.get(fname, [])
        # dictionary keyed by Q value
        hkl_by_q = {}
        for qval,h,k,l in hkl_entries:
            hkl_by_q.setdefault(qval, []).append((h,k,l))
        label_map = cif_hkl_label_map.get(fname, {})
        # --- Optimized tick & hkl label drawing ---
        if show_hkl and peaksQ and label_map:
            # Guard against pathological large peak lists (can freeze UI)
            if len(peaksQ) > 4000 or len(domain_peaks) > 4000:
                print(f"[hkl] Too many peaks in {lab} (>{len(peaksQ)}) – skipping hkl labels. Press 'z' again to toggle off.")
                # still draw ticks below without labels
                effective_show_hkl = False
            else:
                effective_show_hkl = True
        else:
            effective_show_hkl = False

        # Precompute rounding function once
        if effective_show_hkl:
            # For 2θ axis we convert back to Q then round; otherwise Q directly
            for p in domain_peaks:
                ln, = ax.plot([p,p],[y_line, y_line+0.02*yr], color=color, lw=1.0, alpha=0.9, zorder=3)
                new_art.append(ln)
                if use_2th and wl:
                    theta = np.radians(p/2.0)
                    Qp = 4*np.pi*np.sin(theta)/wl
                else:
                    Qp = p
                lbl = label_map.get(round(Qp,6))
                if lbl:
                    t_hkl = ax.text(p, y_line+0.022*yr, lbl, ha='center', va='bottom', fontsize=7, rotation=90, color=color)
                    new_art.append(t_hkl)
        else:
            # Just draw ticks (no hkl labels)
            for p in domain_peaks:
                ln, = ax.plot([p,p],[y_line, y_line+0.02*yr], color=color, lw=1.0, alpha=0.9, zorder=3)
                new_art.append(ln)
        # Removed numbering; keep space padding (placed per CIF row)
        label_text = f" {lab}"
        txt = ax.text(ax.get_xlim()[0], y_line + 0.005*yr, label_text,
                      ha='left', va='bottom', fontsize=max(8,int(0.55*plt.rcParams.get('font.size',12))), color=color)
        new_art.append(txt)
    ax._cif_tick_art = new_art
    # Store simplified metadata for hover: list of dicts with 'x','y','label'
    hover_meta = []
    show_hkl = globals().get('show_cif_hkl', False)
    # Build mapping from Q to label text if available
    for i,(lab, fname, peaksQ, wl, qmax_sim, color) in enumerate(cif_tick_series):
        if use_2th and wl is None:
            wl = getattr(ax, '_cif_hover_wl', None)
        # Recreate domain peaks consistent with those drawn (limit to view)
        if use_2th:
            if wl is None: continue
            domain_peaks = _Q_to_2theta(peaksQ, wl)
        else:
            domain_peaks = peaksQ
        xlow, xhigh = ax.get_xlim()
        domain_peaks = [p for p in domain_peaks if xlow <= p <= xhigh]
        if not domain_peaks:
            continue
        # y baseline for this series (same logic as above)
        if args.stack or len(y_data_list) > 1:
            global_min = min(float(a.min()) for a in y_data_list if len(a)) if y_data_list else ax.get_ylim()[0]
            base = global_min - 0.08*yr; spacing = 0.05*yr
        else:
            global_min = min(float(a.min()) for a in y_data_list if len(a)) if y_data_list else 0.0
            base = global_min - 0.06*yr; spacing = 0.04*yr
        y_line = base - i*spacing
        label_map = cif_hkl_label_map.get(fname, {}) if show_hkl else {}
        for p in domain_peaks:
            if use_2th and wl:
                theta = np.radians(p/2.0); Qp = 4*np.pi*np.sin(theta)/wl
            else:
                Qp = p
            lbl = label_map.get(round(Qp,6), None)
            hover_meta.append({'x': p, 'y': y_line, 'hkl': lbl, 'series': lab})
    ax._cif_tick_hover_meta = hover_meta
    fig.canvas.draw_idle()

    # Install hover handler once
    if not hasattr(ax, '_cif_hover_cid'):
        tooltip = ax.text(0,0,"", va='bottom', ha='left', fontsize=8,
                          color='black', bbox=dict(boxstyle='round,pad=0.2', fc='1.0', ec='0.7', alpha=0.85),
                          visible=False)
        ax._cif_hover_tooltip = tooltip
        def _on_move(event):
            if event.inaxes != ax:
                if tooltip.get_visible():
                    tooltip.set_visible(False); fig.canvas.draw_idle()
                return
            meta = getattr(ax, '_cif_tick_hover_meta', None)
            if not meta:
                if tooltip.get_visible():
                    tooltip.set_visible(False); fig.canvas.draw_idle()
                return
            x = event.xdata; y = event.ydata
            # Find nearest tick within pixel tolerance
            trans = ax.transData
            best = None; best_d2 = 25  # squared pixel distance threshold (5 px)
            for entry in meta:
                px, py = trans.transform((entry['x'], entry['y']))
                ex, ey = trans.transform((x, y))
                d2 = (px-ex)**2 + (py-ey)**2
                if d2 < best_d2:
                    best_d2 = d2; best = entry
            if best is None:
                if tooltip.get_visible():
                    tooltip.set_visible(False); fig.canvas.draw_idle()
                return
            # Compose text
            hkl_txt = best['hkl'] if best.get('hkl') else ''
            tip = f"{best['series']}\nQ={best['x']:.4f}" if use_Q else (f"{best['series']}\n2θ={best['x']:.4f}" if use_2th else f"{best['series']} {best['x']:.4f}")
            if hkl_txt:
                tip += f"\n{hkl_txt}"
            tooltip.set_text(tip)
            tooltip.set_position((best['x'], best['y'] + 0.025*yr))
            if not tooltip.get_visible():
                tooltip.set_visible(True)
            fig.canvas.draw_idle()
        cid = fig.canvas.mpl_connect('motion_notify_event', _on_move)
        ax._cif_hover_cid = cid

if cif_tick_series:
    # Auto-assign distinct colors if all are default 'k'
    if len(cif_tick_series) > 1:
        if all(c[-1] == 'k' for c in cif_tick_series):
            try:
                cmap_name = 'tab10' if len(cif_tick_series) <= 10 else 'hsv'
                cmap = plt.get_cmap(cmap_name)
                new_series = []
                for i,(lab,fname,peaksQ,wl,qmax_sim,col) in enumerate(cif_tick_series):
                    color = cmap(i / max(1,(len(cif_tick_series)-1)))
                    new_series.append((lab,fname,peaksQ,wl,qmax_sim,color))
                cif_tick_series[:] = new_series
            except Exception:
                pass
    if use_2th:
        _ensure_wavelength_for_2theta()
    draw_cif_ticks()
    # expose helpers for interactive updates
    ax._cif_extend_func = extend_cif_tick_series
    ax._cif_draw_func = draw_cif_ticks

if use_E: x_label = "Energy (eV)"
elif use_r: x_label = r"r (Å)"
elif use_k: x_label = r"k ($\mathrm{\AA}^{-1}$)"
elif use_rft: x_label = "Radial distance (Å)"
elif use_Q: x_label = r"Q ($\mathrm{\AA}^{-1}$)"
elif use_2th: x_label = r"$2\theta$ (deg)"
elif args.xaxis:
    x_label = str(args.xaxis)
else:
    x_label = "X"
ax.set_xlabel(x_label, fontsize=16)
if args.raw:
    ax.set_ylabel("Intensity", fontsize=16)
else:
    ax.set_ylabel("Normalized intensity (a.u.)", fontsize=16)

# Store originals for axis-title toggle restoration (t menu bn/ln)
try:
    ax._stored_xlabel = ax.get_xlabel()
    ax._stored_ylabel = ax.get_ylabel()
except Exception:
    pass

# --- FINAL LABEL POSITION PASS ---
# Some downstream operations (e.g. CIF tick overlay extending y-limits or auto margin
# adjustments by certain backends) can occur after the initial label placement,
# leading to visibly misplaced curve labels on first show. We perform a final
# synchronous draw + update_labels here to lock them to the correct coordinates
# before any saving / interactive session starts. (Subsequent interactions still
# use the existing callbacks / update logic.)
try:
    fig.canvas.draw()  # ensure limits are finalized
    update_labels(ax, y_data_list, label_text_objects, args.stack)
except Exception:
    pass

# ---------------- Save figure object ----------------
if args.savefig:
    # Remove numbering for exported figure object (if ticks present)
    if cif_tick_series and 'cif_numbering_enabled' in globals() and cif_numbering_enabled:
        prev_num = cif_numbering_enabled
        cif_numbering_enabled = False
        if 'draw_cif_ticks' in globals():
            draw_cif_ticks()
        target = _confirm_overwrite(args.savefig)
        if target:
            with open(target, "wb") as f:
                pickle.dump(fig, f)
        cif_numbering_enabled = prev_num
        if 'draw_cif_ticks' in globals():
            draw_cif_ticks()
    else:
        target = _confirm_overwrite(args.savefig)
        if target:
            with open(target, "wb") as f:
                pickle.dump(fig, f)
    if target:
        print(f"Saved figure object to {target}")


def main():
    # ---------------- Show and interactive menu ----------------
    if args.interactive:
        # Increase default upper margin (more space): reduce 'top' value once and lock
        try:
            sp = fig.subplotpars
            if sp.top >= 0.88:  # only if near default
                fig.subplots_adjust(top=0.88)
                fig._interactive_top_locked = True
        except Exception:
            pass
        interactive_menu(fig, ax, y_data_list, x_data_list, labels_list,
                         orig_y, label_text_objects, args.delta, x_label, args,
                         x_full_list, raw_y_full_list, offsets_list,
                         use_Q, use_r, use_E, use_k, use_rft)
    elif args.out:
        out_file = args.out
        if not os.path.splitext(out_file)[1]:
            out_file += ".svg"
        # Confirm overwrite for export path
        export_target = _confirm_overwrite(out_file)
        if not export_target:
            print("Export canceled.")
        else:
            for i, txt in enumerate(label_text_objects):
                txt.set_text(labels_list[i])
            # Temporarily disable numbering for export
            if cif_tick_series and 'cif_numbering_enabled' in globals() and cif_numbering_enabled:
                prev_num = cif_numbering_enabled
                cif_numbering_enabled = False
                if 'draw_cif_ticks' in globals():
                    draw_cif_ticks()
                fig.savefig(export_target, dpi=300)
                cif_numbering_enabled = prev_num
                if 'draw_cif_ticks' in globals():
                    draw_cif_ticks()
            else:
                fig.savefig(export_target, dpi=300)
            print(f"Saved plot to {export_target}")
    else:
        # Default: show the plot in non-interactive, non-save mode
        plt.show()


# Entry point for CLI
if __name__ == "__main__":
    main()
