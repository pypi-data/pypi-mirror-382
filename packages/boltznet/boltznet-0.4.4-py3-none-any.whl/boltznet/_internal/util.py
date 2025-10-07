#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
General utility functions for modeling motifs including
- functions for plotting motif logos
- function for mapping promoters to modifications
- functions for plotting results and result comparisons
- functions that work with coverage data

@author: jamesgalagan
"""

import sys
import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import logomaker
import scipy
from sklearn import metrics

from .sequence import letters
from . import sequence
from matplotlib.ticker import FormatStrFormatter, FuncFormatter
from . import aln
from . import CONFIG

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from BCBio.GFF import GFF3Writer

import re


#%% ---------- UTILITY FUNCTIONS -----------------------
def flush_print(msg, flag='STATUS'):
    """Utility function to print 'flag: msg' then flush std out
    useful for log monitoring"""

    print('%s: %s' % (flag, msg))
    sys.stdout.flush()


# -----------------
def prom2mod(prom):
    """Maps a promoter type str to a modification type string"""
    if prom == 'native':
        mod = 'native'
    elif prom == 'in vitro':
        mod = 'in_vitro'
    else:
        mod = 'inducible'

    return mod



# -------------------------------------
def plot_model_results(X, y, yhat, b, bfit):
    """Plot motif comparison and plot y vs yhat"""
    plot_motif_comparison(b, bfit)
    plot_y_vs_yhat(y, yhat)


# -------------------------------------
def plot_motif(m):
    """Plot motif as a heatmap"""
    plt.imshow(m, cmap='coolwarm')
    plt.yticks((0, 1, 2, 3), letters)
    plt.show()


# -------------------------------------
def plot_motif_comparison(b, bfit):
    """Plot a comparison of two motifs as two heatmaps"""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
    # ax1.imshow(b,vmin=-5,vmax=5,cmap='coolwarm')
    ax1.imshow(b, cmap='coolwarm')
    ax1.set_title('True Motif')
    # ax2.imshow(bfit,vmin=-5,vmax=5,cmap='coolwarm')
    ax2.imshow(bfit, cmap='coolwarm')
    ax2.set_title('Predicted Motif')
    ax3.scatter(b, bfit)
    ax3.set_xlabel('Actual')
    ax3.set_ylabel('Predicted')
    ax3.plot(b[:], b[:])
    ax3.plot(b[:], -b[:])
    plt.show()


# -------------------------------------
def plot_y_vs_yhat_grid(y, yhat, **kwargs):
    """Plot a comparison of y vs yhat
    specifically for y and yhat where shape[1]>1
    each column is in its own figure in a grid of figures"""

    nplots = y.shape[1]
    ncols = math.ceil(np.sqrt(nplots))
    nrows = math.floor(np.sqrt(nplots))

    if 'ax' in kwargs:
        ax = kwargs.get('ax')
        fig = ax.get_figure()
    else:
        fig = plt.figure(figsize=(12, 8))

    # labels become figure titles
    titles = []
    if 'labels' in kwargs:
        titles = kwargs.pop('labels')

    # title becomes figure suptitles
    suptit = ''
    if 'title' in kwargs:
        suptit = kwargs.pop('title')

    subfigs = fig.subfigures(nrows, ncols)

    i = 0
    for c in range(ncols):
        for r in range(nrows):
            if nrows > 1:
                ax = subfigs[r, c].subplots(1, 1)
            else:
                ax = subfigs[c].subplots(1, 1)

            plot_y_vs_yhat(y[:, i], yhat[:, i], ax=ax,
                           title=titles[i], **kwargs)
            i = i + 1
            if i == nplots:
                break
        if i == nplots:
            break

    plt.suptitle(suptit)


# -------------------------------------
def plot_y_vs_yhat(y, yhat, ms=8, font_size=12, legend_font_size=6, tick_font=6,xlabel='Actual',ylabel='Predicted', alpha=1,mc=None,neg_gray=False, mse=False,**kwargs):
    """Plot a comparison of y vs yhat
    kwargs include:
        - ax: to provide an existing axis to plot on
        - labels: labels for each element of y
        - firstneg: the index of the first negative value (used for training output)
        - title: a title for the plot"""
    if 'ax' in kwargs:
        ax = kwargs.get('ax')
    else:
        fig, ax = plt.subplots(1, 1)

    if 'colors' in kwargs:
        colors = kwargs.get('colors')
    else:
        colors = []

    if 'neg_ms' in kwargs:
        neg_ms = kwargs.get('neg_ms')
    else:
        neg_ms = ms

    if 'legend_left' in kwargs:
        legend_left = kwargs.get('legend_left')
    else:
        legend_left = False

    
    if 'legend_right' in kwargs:
        legend_right = kwargs.get('legend_right')
    else:
        legend_right = False
    if 'legend_up' in kwargs:
        legend_up = kwargs.get('legend_up')
    else:
        legend_up = False
        
    legend_cols=kwargs.get('legend_cols',2)    
    markeredgewidth=kwargs.get('markeredgewidth',1)

    if len(y.shape) == 2:
        if 'labels' in kwargs:
            labels = kwargs.get('labels')
        else:
            labels = [str(i) for i in range(y.shape[1])]

        for i in range(y.shape[1]):

            if mc is None and len(colors) == 0:
                ax.plot(y[:, i], yhat[:, i], '.', label=labels[i], markersize=ms,alpha=alpha,markeredgewidth=markeredgewidth)
            elif mc is not None:
                ax.plot(y[:, i], yhat[:, i], '.', label=labels[i], markersize=ms,alpha=alpha,c=mc,markeredgewidth=markeredgewidth)
            else:
                ax.plot(y[:, i], yhat[:, i], '.', label=labels[i], markersize=ms,alpha=alpha,c=colors[i],markeredgewidth=markeredgewidth)

            

        if legend_font_size>0:
            if legend_right:
                ax.legend(fontsize=legend_font_size, frameon=False, ncol=legend_cols, loc='lower right', bbox_to_anchor=(-0.3, 1.2))
            elif legend_left:
                ax.legend(fontsize=legend_font_size, frameon=False, ncol=legend_cols, loc='upper left', bbox_to_anchor=(1, 1.2))
            elif legend_up:
                ax.legend(fontsize=legend_font_size, frameon=False, ncol=legend_cols, loc='upper left', bbox_to_anchor=(-0.025, 1))
            else:
                ax.legend(fontsize=legend_font_size,frameon=False,ncol=legend_cols)

    else:
        ax.plot(y, yhat, '.',c=mc,alpha=alpha,markersize=ms,markeredgewidth=markeredgewidth)

    if mse:  #calculate mse and add to plot
        mse_val=metrics.mean_squared_error(y,yhat)
        ax.text(0.1, 0.94, "MSE = %.2e"%mse_val,
                transform=ax.transAxes,
                fontsize=16,
                verticalalignment='top',
                horizontalalignment='left',
                fontweight='normal',
                )

    ax.plot(yhat, yhat, c="black",alpha=alpha,markeredgewidth=markeredgewidth)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis='both', which='major', labelsize=tick_font)
    ax.xaxis.label.set_fontsize(font_size)
    ax.yaxis.label.set_fontsize(font_size)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    
    # ax.set_ylim([None, np.amax(yhat) + .1])
    # ax.set_xlim([None, np.amax(yhat) + .1])
    
    
    if 'firstneg' in kwargs:
        ii = kwargs.get('firstneg')
        last = len(y) - 1

        if neg_gray:
            ax.plot(y[ii:last], yhat[ii:last], 'o', markersize=neg_ms,alpha=alpha, c='gray',markeredgewidth=markeredgewidth)
        else:
            ax.plot(y[ii:last], yhat[ii:last], 'bo', markersize=neg_ms,alpha=alpha,markeredgewidth=markeredgewidth)

    if 'title' in kwargs:
        tit = kwargs.get('title')
        ax.set_title(tit)
        ax.title.set_fontsize(font_size)
        


# -------------------------------------
def plot_test_data(d, lbls):
    """Plot test data"""
    fig, axs = plt.subplots(1, len(d))

    for i in range(len(d)):
        axs[i].plot(d[i], 'ro')
        axs[i].title.set_text(lbls[i])

    plt.show()


# -------------------------------------
def plot_rand_samples(dat, num):
    """Plot random samples"""
    ind = np.random.randint(0, dat.shape[0], (num, 1))

    for i in range(num):
        plt.subplot(10, np.ceil(num / 10), i + 1)

        if dat.ndim == 2:
            plt.plot(dat[ind[i, 0], :], 'ro')
            plt.title(ind[i, 0])
        elif dat.ndim == 1:
            plt.plot(dat[ind[i, 0]], 'ro')
            plt.title(ind[i, 0])

        elif dat.ndim > 2:
            d = dat[ind[i, 0], :, :]
            d = np.reshape(d, (d.shape[0], d.shape[1]))
            plt.imshow(d)
            plt.title(ind[i, 0])

    plt.show()


# -------------------------------------
def run_gv(path='./GenomeView.jnlp'):
    """Run GenomeView using a system open call"""
    os.system('open %s' % path)


# -------------------------------------
def getRegulonDBPFMs(regulon_dir=CONFIG.new_regulon_dir,tfs=[]):
    '''Get a the Known PFMS from Regulon DB'''

    [pssm, pfms, tfs_pssm, tf_n] = aln.read_meme(regulon_dir,tfs=tfs)

    regDB={}
    for n,f in zip(tfs_pssm,pfms):
        
        #lower case the first letter
        name=res = n[0].lower() + n[1:]
        
        regDB[name]=f

    return regDB

# -------------------------------------
def window_sum(val, winsize, stepsize=-1):
    """ given any np array (len,dims) of data points
    take each winsize of data points and calculate sum
    then step stepsize data points and repeat until end
    (if stepsize=-1, default, then stepsize=winsize)
    remainder vals are ignored"""

    if stepsize == -1:
        stepsize = winsize

    if len(val.shape) == 1:
        val = np.reshape(val, (val.shape[0], 1))

    rng = range(0, val.shape[0], stepsize)
    wvals = np.zeros((len(rng), val.shape[1]))

    i = 0
    for p in rng:
        for j in range(val.shape[1]):
            wvals[i, j] = np.sum(val[p:p + winsize, j])
        i = i + 1

    return wvals


# -------------------------------------
def window_max(val, winsize, stepsize=-1):
    """ given any np array (len,dims) of data points
    take each winsize of data points and calculate max
    then step stepsize data points and repeat until end
    (if stepsize=-1, default, then stepsize=winsize)
    remainder vals are ignored"""

    if stepsize == -1:
        stepsize = winsize

    if len(val.shape) == 1:
        val = np.reshape(val, (val.shape[0], 1))

    rng = range(0, val.shape[0], stepsize)
    wvals = np.zeros((len(rng), val.shape[1]))

    i = 0
    for p in rng:
        for j in range(val.shape[1]):
            wvals[i, j] = np.max(val[p:p + winsize, j])
        i = i + 1

    return wvals


# -------------------------------------
def window_ave(val, winsize, stepsize=-1):
    """given any np array (len,dims) of data points
    take each winsize of data points and calculate ave
    then step stepsize data points and repeat until end
    (if stepsize=-1, default, then stepsize=winsize)
    remainder vals are ignored
    """

    if stepsize == -1:
        stepsize = winsize

    if len(val.shape) == 1:
        val = np.reshape(val, (val.shape[0], 1))

    rng = range(0, val.shape[0], stepsize)
    wvals = np.zeros((len(rng), val.shape[1]))

    i = 0
    for p in rng:
        for j in range(val.shape[1]):
            wvals[i, j] = np.mean(val[p:p + winsize, j])
        i = i + 1

    return wvals


# -------------------------------------
def cov2accuracy(cov, pred, th=0.04):
    """Return accuracy stats given coverage and predictions.

    given true cov: cov
    and predicted cov: pre
    return binary accuracy measures given th
    cov/pred > th == 1, 0 o/w
    and also the r-squared of the linear regression fit
    if cov and pred have multiple columns the data a considered as a whole
    """

    if len(cov.shape) == 1:
        cov = np.reshape(cov, (cov.shape[0], 1))
    else:
        cov = np.reshape(cov, (cov.shape[0] * cov.shape[1], 1))

    if len(pred.shape) == 1:
        pred = np.reshape(pred, (pred.shape[0], 1))
    else:
        pred = np.reshape(pred, (pred.shape[0] * pred.shape[1], 1))

    # spec = 0
    # sens = 0

    bcov = np.zeros(cov.shape[0])
    bpred = np.zeros(cov.shape[0])

    ind_pos = np.where(cov > th)
    bcov[ind_pos[0]] = 1

    ind = np.where(pred > th)
    bpred[ind[0]] = 1

    # sens is number of bcov>0 where bpred>0 or TP/P
    pos = np.where(bcov > 0)[0]
    npos = len(pos)

    tp = np.where(bpred[pos] > 0)[0]
    ntp = len(tp)
    if npos == 0:
        sens = float('nan')
    else:
        sens = ntp / npos

    # spec is number of bcov==0 where bpred==0 or TN/N
    neg = np.where(bcov == 0)[0]
    nneg = len(neg)

    tn = np.where(bpred[neg] == 0)[0]
    ntn = len(tn)
    if nneg > 0:
        spec = ntn / nneg
    else:
        spec = 0

    # AUC
    fpr, tpr, thresholds = metrics.roc_curve(bcov, pred)
    auc = metrics.auc(fpr, tpr)

    # r-squared of linear regression
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(
        cov[:, 0], pred[:, 0])
    rsq = r_value ** 2

    stats = pd.DataFrame(data=[[sens, spec, auc, rsq, slope, intercept, p_value]],
                         columns=['sens', 'spec', 'auc', 'rsq', 'slope', 'intercept', 'pval'])

    return stats


#---------------------------------------------
def sort_labels(label):
    """
    Provides a default behavior for sorting a sample name df from ecoliDB.getSampleNameColormap
    Returns a tuple of (primary, secondary) sort values, where primary corresponds to experiment type,
    and secondary a replicate number.
    Sorts native experiments first, in ascending rep # order, then inducible, then invitro (1x then 10x).
    If labels have non-replicate endings (e.g. pyr, glyox), those come at the end of the primary sort
    """
    components = label.split()

    primary_order = {'native': 0, 'inducible': 1, 'in vitro': 2}

    # Sort by concentration (lower first) then replicate
    if 'in vitro' in label:
        primary_val = 2
        concentration = components[3]
        replicate = components[4]
        conc_val = int(concentration.replace('x', '').replace('X', ''))
        rep_val = int(replicate)
        return (primary_val, conc_val, rep_val)
    
    # Native first, then by replicate # (or type)
    primary_val = primary_order[components[1]]
    try:
        # In case the "replicate" is something like pyr
        secondary_val = int(components[2])
    except ValueError:
        secondary_val = float('inf')
    
    return (primary_val, secondary_val)


#---------------------------------------------
def sort_sample_name_map(sdf, sample_ids = None, sample_names = None):
    """
    Given a sample name df from ecoliDB.getSampleNameColorMap, sort the dataframe
    by:
        1) a list of sample_ids (these happen to be unique in the project but the run/sample pair doesn't require that to be the case)
        2) a list of sample_names (these correspond to what we submitted to GEO & can be used for plot labels)
        3) start with native 1,2...N; inducible 1,2...N; iv 1x, 10x

    Returns the sorted dataframe and may omit samples if not provided in sample_ids/names
    """

    if sample_ids is not None or sample_names is not None:
        # If both are provided, use sample_id first
        if sample_ids is not None:
            sort_key = 'sample_id'
            sort_list = sample_ids
        else:
            sort_key = 'sample_name'
            sort_list = sample_names
        
        # Make dict to map sort values to indices
        sort_mapping = {val: ind for ind, val in enumerate(sort_list)}
        
        # Only return items that were given 
        tmp_df = sdf[sdf[sort_key].isin(sort_list)]
        return tmp_df.sort_values(by=sort_key, key=lambda x: x.map(sort_mapping))
    
    return sdf.sort_values(by='sample_name', key=lambda col: col.map(sort_labels))
    

#---------------------------------------------
def doc_dict(d,indent=0):
    '''Function to recursively document a dictionary'''
    
    for key, value in d.items():
        # Print the key with indentation
        print('  ' * indent + f"- {key}: ", end="")
        
        # Check the type of the value
        if isinstance(value, dict):
            print("Nested dictionary:")
            doc_dict(value, indent + 1)
        elif isinstance(value, list):
            print(f"List with {len(value)} elements")
            if len(value) > 0 and isinstance(value[0], dict):
                print('  ' * (indent + 1) + "Structure of items:")
                doc_dict(value[0], indent + 2)
        elif isinstance(value, np.ndarray):
            
            print("Numpy Array: shape=%s "%str(value.shape))
        elif isinstance(value,pd.Series):

            print("Panda Series: len=%i "%len(value))
        
        else:
            print(f"Type: {type(value).__name__}")
    

#%% ---------- FILE LOADING AND SAVING FUNCTIONS -----------------------
# useful for handling common filetypes in a uniform way across the codebase

def read_wig_file(fname):
    """Read a wig file into a numpy array"""
    fp = open(fname)
    lines = fp.readlines()

    data = [[int(v) for v in line.split()] for line in lines]
    data = np.array(data)

    fp.close()
    return data

def load_annot_gff(gff_file):
    """
    Loads a GFF3 file into a dict: seqid -> DataFrame with columns
    ['type','ID','name','symbol','start','stop','strand','source'].
    
    """
    seqid_to_rows = {}

    with open(gff_file) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue

            cols = line.rstrip("\n").split("\t")
            if len(cols) != 9:
                continue  # skip malformed lines

            seqid, source, ftype, start, stop, score, strand, phase, attributes = cols

            # Parse attributes
            attr_dict = {}
            for field in attributes.split(";"):
                if not field:
                    continue
                if "=" in field:
                    key, value = field.split("=", 1)
                    attr_dict[key] = value

            name = attr_dict.get("Name")
            gene = attr_dict.get("gene")
            _id  = attr_dict.get("ID")
            symbol = name or gene or _id

            row = {
                "type":   ftype,
                "ID":     _id,
                "name":   name,
                "symbol": symbol,
                "start":  int(start),
                "stop":   int(stop),
                "strand": strand,   # '+', '-', or '.'
                "source": source
            }
            seqid_to_rows.setdefault(seqid, []).append(row)

    annot_dict = {seqid: pd.DataFrame(rows) for seqid, rows in seqid_to_rows.items()}
    return annot_dict


def export_annot_gff(ddf, filename):
    """
    Given a dict: seqid -> DataFrame with columns
    ['type','ID','name','start','stop','strand','source'] (symbol optional),
    export to a GFF3 file.
    """
    # map GFF strand char to Biopython strand value
    def biopy_strand(s):
        if s == '+': return +1
        if s == '-': return -1
        return None  # '.' or None

    seqrecs = []

    for seqid, df in ddf.items():
        # Ensure required columns exist (fill with None if missing)
        for col in ["type", "ID", "name", "start", "stop", "strand", "source"]:
            if col not in df.columns:
                df[col] = None

        rec = SeqRecord(Seq(""), id=str(seqid), description="")

        for _, row in df.iterrows():
            try:
                start = int(row["start"])
                stop  = int(row["stop"])
            except Exception:
                continue  # skip rows with bad coords

            loc = FeatureLocation(start - 1, stop, strand=biopy_strand(row["strand"]))
            quals = {}

            # only include qualifiers that exist
            if pd.notna(row.get("ID")):
                quals["ID"] = [str(row["ID"])]
            if pd.notna(row.get("name")):
                quals["Name"] = [str(row["name"])]
            if pd.notna(row.get("source")):
                quals["source"] = [str(row["source"])]
            if "symbol" in df.columns and pd.notna(row.get("symbol")) and row.get("symbol") != row.get("name"):
                # add symbol if distinct from name
                quals["symbol"] = [str(row["symbol"])]

            feat = SeqFeature(location=loc, type=str(row["type"] or "feature"), qualifiers=quals)
            rec.features.append(feat)

        seqrecs.append(rec)

    # Write once, after building all SeqRecords
    with open(filename, "w") as out_handle:
        writer = GFF3Writer()
        writer.write(seqrecs, out_handle)

def load_seqs_from_fasta(seqfile):
    ''' Load a set of sequences from a fasta file and returns sequences, onehot,
    seqids, and seq positions
    
    Headers are expected to have the form
    
    >seqname description
    
    And if description contains the following text
     
    (start=<seqpos_start>, end=<seqpos_end>)
    
    then seqpos is parsed out as a tuple, otherwise seqpos is none
    
    Return a dictionary of dictionaries
    
    seqid => {'seq':seq, 'onehot':onehot, 'pos': seqpos)
    
    '''
    # all sequences must be same lenght


    seqdict={}
    for record in SeqIO.parse(seqfile, "fasta"):
        s =str(record.seq)
            
        s1 = sequence.str2onehot(s)
        
        sid=record.id
        
        # parse the description for seqpos
        match = re.search(r"\(start=(\d+),\s*end=(\d+)\)", record.description)
        if match:
            seqpos=(int(match.group(1)), int(match.group(2)))
        else:
            seqpos=None
        
        seqdict[sid]={'seq':s,'onehot':s1,'pos':seqpos}

    return seqdict


def export_seqdict_to_fasta(seqdict, fasta_path):
    """
    Export a dict of seqs to FASTA.

    seqdict format:
        {
          seqid: {
            'seq': <str>,
            'onehot': <...>,   # ignored here
            'pos': (start, end)
          },
          ...
        }

    FASTA header:
        >seqid_with_underscores (start=<start>, end=<end>)
    """
    records = []
    for seqid, d in seqdict.items():
        s = d.get('seq')
        pos = d.get('pos')
        if s is None or pos is None or len(pos) != 2:
            # skip malformed entries
            continue

        clean_id = str(seqid).replace(" ", "_")
        start, end = int(pos[0]), int(pos[1])
        desc = f"(start={start}, end={end})"

        records.append(SeqRecord(Seq(str(s)), id=clean_id, description=desc))

    # write to FASTA
    SeqIO.write(records, fasta_path, "fasta")
    
    return len(records)      

def load_genbank(gbk_file):
    """
    Parse a GenBank file into:
      annot_dict: seqid -> DataFrame with columns
        ['type','ID','name','symbol','start','stop','strand','source']
      seqdict:    seqid -> {'seq': <str>, 'onehot': <ndarray>, 'pos': (1, seqlen)}

    Returns annot_dict, seqdict
    Notes:
      - Positions are 1-based inclusive (to match your GFF loader’s convention).
      - Strand is '+', '-', or '.'.
      - 'ID' prefers /locus_tag, then /gene, then /protein_id; falls back to a constructed ID.
      - 'name' prefers /gene, then /product, else None.
      - 'symbol' = name or ID.
      - All features are included (gene, CDS, mRNA, misc_feature, etc.).
    """
    annot_dict = {}
    seqdict = {}

    def _first(q, key):
        """Return first qualifier value if present, else None."""
        vals = q.get(key)
        if not vals:
            return None
        return vals[0] if isinstance(vals, list) else vals

    def _feat_id(qualifiers, fallback_prefix="feat"):
        # Prefer locus_tag, then gene, then protein_id, else None
        return (_first(qualifiers, "locus_tag")
                or _first(qualifiers, "gene")
                or _first(qualifiers, "protein_id")
                or None)

    def _feat_name(qualifiers):
        # Prefer gene symbol, then product
        return _first(qualifiers, "gene") or _first(qualifiers, "product")

    def _strand_symbol(strand_val):
        return "+" if strand_val == 1 else "-" if strand_val == -1 else "."

    for rec in SeqIO.parse(gbk_file, "genbank"):
        seqid = rec.id  # e.g., locus or accession
        seqlen = len(rec.seq)

        # Build sequence dict entry
        s = str(rec.seq)
        onehot = sequence.str2onehot(s)
        seqdict[seqid] = {"seq": s, "onehot": onehot, "pos": (1, seqlen)}

        rows = []
        default_source = rec.annotations.get("source") or "GenBank"

        for i, feat in enumerate(rec.features):
            # Compute 1-based inclusive coordinates from Biopython locations (0-based, end-exclusive)
            try:
                start_1 = int(feat.location.start) + 1
                stop_1  = int(feat.location.end)
            except Exception:
                # Fallback for fuzzy/unknown locations
                start_1, stop_1 = (1, seqlen)

            qualifiers = feat.qualifiers or {}
            fid = _feat_id(qualifiers) or f"{feat.type}_{i+1}"
            name = _feat_name(qualifiers)
            symbol = name or fid
            strand = _strand_symbol(getattr(feat.location, "strand", None))
            source = _first(qualifiers, "source") or default_source

            rows.append({
                "type":   feat.type,   # e.g., 'gene', 'CDS', 'mRNA', 'misc_feature'
                "ID":     fid,
                "name":   name,
                "symbol": symbol,
                "start":  int(start_1),
                "stop":   int(stop_1),
                "strand": strand,
                "source": source
            })

        annot_dict[seqid] = pd.DataFrame(rows, columns=[
            "type","ID","name","symbol","start","stop","strand","source"
        ])

    return annot_dict, seqdict



#%% ------------ PLOTTING SEQLOGOS ---------------

def plot_info_logo(df, **kwargs):
    """ Plot a logo based on the information content of the motif
        plot_info_logo(df,**kwargs)
            df is an nd array of shape (4,mlen) - order of sequnces based on sequence.letters
            kwargs optional arguments are those for plot_logo
        """

    df = np.transpose(df)
    df = pd.DataFrame(data=df, columns=letters)
    df = logomaker.transform_matrix(
        df, from_type='probability', to_type='information')
    df = np.transpose(df)

    plot_logo(df, ylim=[0, 2], **kwargs)


# -------------------------------------
def plot_exp_logo(df, **kwargs):
    """Exponentiate a logo and then plot the logo
    See plot_logo for input format information"""
    df = np.exp(df)
    plot_logo(df, **kwargs)


# -------------------------------------
def plot_seq_logo(s, **kwargs):
    """Takes a sequence and plots it as a logo
    input expects a 4 dim tensor of shape [1,4,slen,1]"""
    ss = np.reshape(s, (4, s.shape[2]))
    # print(ss.shape)
    
    plot_logo(ss, **kwargs)


# -------------------------------------
def plot_logo(df, fig=None, ax=None, **kwargs):
    """ Plot a logo based on the information content of the motif df
        plot_logo(df,**kwargs)
            df is an nd array of shape (4,mlen) - order of sequnces based on sequence.letters
            kwargs optional arguments
            - ax to plot on axis
            - title to add title to plot
            - highlightRegion - a list of [start,stop] pairs to highlight portions of the plot
            - reverse makes highlights lime, cyan otherwise
            - score adds a line plot of score to the plot
            - colors is a dictionary of colors - default is
                     {'A': [1, 0, 0],
                      'T': [0, 0.5, 0],
                      'C': [0, 0, 1],
                      'G': [1, 0.65, 0]}
            -Can also highlight bases by passing a binary array where a 1 corresponds to the position of mutation as 'highlight_bases'
        """
    if fig is None and ax is None:
        fig=plt.figure(figsize=(12,8))
    
    if ax is None:
        ax=fig.subplots(1,1)

    tit = ''
    if 'title' in kwargs:
        tit = kwargs.get('title')

    if 'highlightRegion' in kwargs:
        highlight = kwargs.get('highlightRegion')
    else:
        highlight = []

    if 'reverse' in kwargs:
        reverse = kwargs.get('reverse')
    else:
        reverse = False

    if 'score' in kwargs:
        score = kwargs.get('score')

    # to match meme
    if 'colors' in kwargs:
        colors=kwargs.get('colors')
    else:
        colors = {'A': [1, 0, 0],
              'T': [0, 0.5, 0],
              'C': [0, 0, 1],
              'G': [1, 0.65, 0]}
        
    if 'fs' in kwargs:
        fontsize=kwargs.get('fs')
    else:
        fontsize=17

    if 'fontweight' in kwargs:
        fontweight=kwargs.get('fontweight')
    else:
        fontweight='normal'

    if 'fontfamily' in kwargs:
        fontfamily=kwargs.get('fontfamily')
    else:
        fontfamily=None

    df = np.transpose(df)
    # df=np.exp(df)

    df = pd.DataFrame(data=df, columns=letters)
    

    # print(df)

    # create Logo object
    
    crp_logo = logomaker.Logo(df,
                              ax=ax,
                              color_scheme=colors,
                              shade_below=0,
                              fade_below=0,
                              flip_below=False,
                              baseline_width=0,
                              font_name='Arial Rounded MT Bold')
    #Highlight Bases
    if kwargs.get('highlight_bases',None) is not None:
        for x, flag in enumerate(kwargs.get('highlight_bases')):
            if flag == 1:
                crp_logo.highlight_position(x, color='yellow')


        


    crp_logo.style_xticks(rotation=90, fmt='%d', spacing=2, anchor=0)

    crp_logo.ax.set_title(tit, fontsize=fontsize, fontweight=fontweight,fontfamily=fontfamily)
        
    if 'show_pos' in kwargs:
        crp_logo.style_spines(spines=['bottom'], visible=True)
        crp_logo.ax.set_xticks(range(0,len(df),10))
        crp_logo.ax.set_xticklabels('%d'%x for x in range(0,len(df),10))
        
    
    if 'ylabel' in kwargs:
        crp_logo.ax.set_ylabel(kwargs.get('ylabel'),fontsize=fontsize,labelpad=-15,fontfamily=fontfamily)
        
    if 'xlabel' in kwargs:
        crp_logo.ax.set_xlabel(kwargs.get('xlabel'),fontsize=fontsize,fontfamily=fontfamily)

    if 'ylim' in kwargs:
        crp_logo.ax.set_ylim(kwargs.get('ylim'))

    if reverse:
        color = '#f14cc1'
    else:
        color = '#00d7ff'

    if highlight is not None and len(highlight) > 0:
        for h in highlight:
            crp_logo.highlight_position_range(
                pmin=int(h[0]), pmax=int(h[1]), color=color, alpha=0.2)
      
    if 'baseline' in kwargs:
        crp_logo.draw_baseline(y = kwargs.get('baseline'), lw = 2)

    if 'score' in kwargs:
        ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
        color = 'black'
        # ax2.plot(score, color=color, linewidth=8)
        ax2.plot(score, color=color, markersize=30, linewidth=3, marker="*")
        ax2.tick_params(axis='y', labelcolor=color)
    if 'tick_font' in kwargs:
        tick_font = kwargs.get('tick_font')
        ax.tick_params(axis='both', which='major', labelsize=tick_font)
        # ax.yaxis.set_major_formatter(FormatStrFormatter('%6.d'))
    
    # this makes sure that all yaxes line up even if labels are diff lengths
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda x, pos: f"{x:>5.0f}".replace(" ", "\u2007"))
    )
    # plt.show()


    
