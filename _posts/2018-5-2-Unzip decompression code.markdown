---
layout: post
title: unzip解压部分代码
date: 发布于2018-05-02 18:57:47 +0800
categories: 测试结果杂记
tag: 4
---

* content
{:toc}

朋友，你的代码里需要处理zip文件吗？你是不是也觉得直接调用unzip命令效率非常低吗？那还等什么？赶快拿起键盘，按下复制粘贴键搬运吧！！！

<!-- more -->

说明：代码只做示例之用，只能处理压缩包里只有一个文件的情况，直接读取第一个压缩文件的数据，调用解压算法进行解压，简单粗暴，如果想处理多个文件的压缩包，请自行查阅zip文件的中央目录的结构。解压算法直接从unzip源码里抠出来的，删除了所有条件编译，不同平台下可能会有不同的结果，目前只在centos6.5下测试通过，其他平台请参考unzip的源码，关于zip文件结构，请参考下面的连接

https://en.wikipedia.org/wiki/Zip_(file_format)

https://pkware.cachefly.net/webdocs/APPNOTE/APPNOTE-6.2.0.txt

http://lib.yoekey.com/?p=236

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <stdint.h>
    #include <string.h>
    
    
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <unistd.h>
    #include <fcntl.h>
    
    
    #ifndef O_BINARY
    #  define O_BINARY  0
    #endif
    
    
    typedef void zvoid;
    typedef unsigned char   uch;    /* code assumes unsigned bytes; these type-  */
    typedef unsigned short  ush;    /*  defs replace byte/UWORD/ULONG (which are */
    typedef unsigned long   ulg;    /*  predefined on some systems) & match zip  */
    
    
    #define DUMPBITS(n) {b>>=(n);k-=(n);}
    
    
    #define MAXLITLENS 288
    #define MAXDISTS 32
    
    
    #define ZCONST const
    
    
    #define UINT_D64 unsigned
    
    
    #define BMAX 16         /* maximum bit length of any code (16 for explode) */
    #define N_MAX 288       /* maximum number of codes in any set */
    
    
    #define WSIZE   65536L  /* window size--must be a power of two, and */
    #define wsize WSIZE       /* wsize is a constant */
    
    
    #define INVALID_CODE 99
    #define IS_INVALID_CODE(c)  ((c) == INVALID_CODE)
    
    
    #  define memzero(dest,len)      memset(dest,0,len)
    
    
    /* bits in base literal/length lookup table */
    static ZCONST unsigned lbits = 9;
    /* bits in base distance lookup table */
    static ZCONST unsigned dbits = 6;
    
    
    static ZCONST unsigned border[] = {
    	16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15 };
    /* - Copy lengths for literal codes 257..285 */
    
    
    static ZCONST ush cplens64[] = {
    	3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31,
    	35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 3, 0, 0 };
    /* For Deflate64, the code 285 is defined differently. */
    
    
    static ZCONST ush cplens32[] = {
    	3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31,
    	35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258, 0, 0 };
    /* note: see note #13 above about the 258 in this list. */
    /* - Extra bits for literal codes 257..285 */
    
    
    static ZCONST uch cplext64[] = {
    	0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2,
    	3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 16, INVALID_CODE, INVALID_CODE };
    
    
    static ZCONST uch cplext32[] = {
    	0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2,
    	3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0, INVALID_CODE, INVALID_CODE };
    
    
    
    
    /* - Extra bits for distance codes 0..29 (0..31 for Deflate64) */
    static ZCONST uch cpdext64[] = {
    	0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6,
    	7, 7, 8, 8, 9, 9, 10, 10, 11, 11,
    	12, 12, 13, 13, 14, 14 };
    
    
    static ZCONST uch cpdext32[] = {
    	0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6,
    	7, 7, 8, 8, 9, 9, 10, 10, 11, 11,
    	12, 12, 13, 13, INVALID_CODE, INVALID_CODE };
    
    
    static ZCONST ush cpdist[] = {
    	1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193,
    	257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145,
    	8193, 12289, 16385, 24577, 32769, 49153 };
    static ZCONST unsigned mask_bits[17] = {
    	0x0000,
    	0x0001, 0x0003, 0x0007, 0x000f, 0x001f, 0x003f, 0x007f, 0x00ff,
    	0x01ff, 0x03ff, 0x07ff, 0x0fff, 0x1fff, 0x3fff, 0x7fff, 0xffff
    };
    
    
    struct huft {
    	uch e;                /* number of extra bits or operation */
    	uch b;                /* number of bits in this code or subcode */
    	union {
    		ush n;            /* literal, length base, or distance base */
    		struct huft *t;   /* pointer to next level of table */
    	} v;
    };
    
    
    typedef struct Globals {
    	int bb, bk, wp, incnt;
    	ZCONST ush *cplens;
    	ZCONST uch *cplext;
    	ZCONST uch *cpdext;
    	struct huft *fixed_tl32;            /* inflate static */
    	struct huft *fixed_td32;            /* inflate static */
    	unsigned fixed_bl32, fixed_bd32;    /* inflate static */
    	struct huft *fixed_tl;
    	unsigned fixed_bl;
    	struct huft *fixed_td;
    	unsigned fixed_bd;
    
    
    	int blockno;
    	unsigned char *inptr;
    	unsigned char *outptr;
    	uch Slide[WSIZE];
    } Uz_Globs;
    
    
    
    
    
    
    #define NEXTBYTE  (G->incnt-- > 0 ? (int)(*G->inptr++) : EOF)
    
    
    #define NEEDBITS(n) {while((int)k<(int)(n)){int c=NEXTBYTE;\
    	if(c==EOF){if((int)k>=0)break;retval=1;goto cleanup_and_exit;}\
    	b|=((ulg)c)<<k;k+=8;}}
    
    
    static void init_global_variables(Uz_Globs *G)
    {
    	memset(G, 0, sizeof(Uz_Globs));
    }
    
    
    static int huft_free(struct huft *t)/* table to free */
    {
    	register struct huft *p, *q;
    
    
    
    
    	/* Go through linked list, freeing from the malloced (t[-1]) address. */
    	p = t;
    	while (p != (struct huft *)NULL)
    	{
    		q = (--p)->v.t;
    		free((zvoid *)p);
    		p = q;
    	}
    	return 0;
    }
    
    
    static int huft_build(
    	ZCONST unsigned *b,   /* code lengths in bits (all assumed <= BMAX) */
    	unsigned n,           /* number of codes (assumed <= N_MAX) */
    	unsigned s,           /* number of simple-valued codes (0..s-1) */
    	ZCONST ush *d,        /* list of base values for non-simple codes */
    	ZCONST uch *e,        /* list of extra bits for non-simple codes */
    	struct huft **t,      /* result: starting table */
    	unsigned *m           /* maximum lookup bits, returns actual */
    )
    {
    	unsigned a;                   /* counter for codes of length k */
    	unsigned c[BMAX + 1];           /* bit length count table */
    	unsigned el;                  /* length of EOB code (value 256) */
    	unsigned f;                   /* i repeats in table every f entries */
    	int g;                        /* maximum code length */
    	int h;                        /* table level */
    	register unsigned i;          /* counter, current code */
    	register unsigned j;          /* counter */
    	register int k;               /* number of bits in current code */
    	int lx[BMAX + 1];               /* memory for l[-1..BMAX-1] */
    	int *l = lx + 1;                /* stack of bits per table */
    	register unsigned *p;         /* pointer into c[], b[], or v[] */
    	register struct huft *q;      /* points to current table */
    	struct huft r;                /* table entry for structure assignment */
    	struct huft *u[BMAX];         /* table stack */
    	unsigned v[N_MAX];            /* values in order of bit length */
    	register int w;               /* bits before this table == (l * h) */
    	unsigned x[BMAX + 1];           /* bit offsets, then code stack */
    	unsigned *xp;                 /* pointer into x */
    	int y;                        /* number of dummy codes added */
    	unsigned z;                   /* number of entries in current table */
    
    
    
    
    								  /* Generate counts for each bit length */
    	el = n > 256 ? b[256] : BMAX; /* set length of EOB code, if any */
    	memzero((char *)c, sizeof(c));
    	p = (unsigned *)b;  i = n;
    	do {
    		c[*p]++; p++;               /* assume all entries <= BMAX */
    	} while (--i);
    	if (c[0] == n)                /* null input--all zero length codes */
    	{
    		*t = (struct huft *)NULL;
    		*m = 0;
    		return 0;
    	}
    
    
    
    
    	/* Find minimum and maximum length, bound *m by those */
    	for (j = 1; j <= BMAX; j++)
    		if (c[j])
    			break;
    	k = j;                        /* minimum code length */
    	if (*m < j)
    		*m = j;
    	for (i = BMAX; i; i--)
    		if (c[i])
    			break;
    	g = i;                        /* maximum code length */
    	if (*m > i)
    		*m = i;
    
    
    
    
    	/* Adjust last length count to fill out codes, if needed */
    	for (y = 1 << j; j < i; j++, y <<= 1)
    		if ((y -= c[j]) < 0)
    			return 2;                 /* bad input: more codes than bits */
    	if ((y -= c[i]) < 0)
    		return 2;
    	c[i] += y;
    
    
    
    
    	/* Generate starting offsets into the value table for each length */
    	x[1] = j = 0;
    	p = c + 1;  xp = x + 2;
    	while (--i) {                 /* note that i == g from above */
    		*xp++ = (j += *p++);
    	}
    
    
    
    
    	/* Make a table of values in order of bit lengths */
    	memzero((char *)v, sizeof(v));
    	p = (unsigned *)b;  i = 0;
    	do {
    		if ((j = *p++) != 0)
    			v[x[j]++] = i;
    	} while (++i < n);
    	n = x[g];                     /* set n to length of v */
    
    
    
    
    								  /* Generate the Huffman codes and for each, make the table entries */
    	x[0] = i = 0;                 /* first Huffman code is zero */
    	p = v;                        /* grab values in bit order */
    	h = -1;                       /* no tables yet--level -1 */
    	w = l[-1] = 0;                /* no bits decoded yet */
    	u[0] = (struct huft *)NULL;   /* just to keep compilers happy */
    	q = (struct huft *)NULL;      /* ditto */
    	z = 0;                        /* ditto */
    
    
    								  /* go through the bit lengths (k already is bits in shortest code) */
    	for (; k <= g; k++)
    	{
    		a = c[k];
    		while (a--)
    		{
    			/* here i is the Huffman code of length k bits for value *p */
    			/* make tables up to required level */
    			while (k > w + l[h])
    			{
    				w += l[h++];            /* add bits already decoded */
    
    
    										/* compute minimum size table less than or equal to *m bits */
    				z = (z = g - w) > *m ? *m : z;                  /* upper limit */
    				if ((f = 1 << (j = k - w)) > a + 1)     /* try a k-w bit table */
    				{                       /* too few codes for k-w bit table */
    					f -= a + 1;           /* deduct codes from patterns left */
    					xp = c + k;
    					while (++j < z)       /* try smaller tables up to z bits */
    					{
    						if ((f <<= 1) <= *++xp)
    							break;            /* enough codes to use up j bits */
    						f -= *xp;           /* else deduct codes from patterns */
    					}
    				}
    				if ((unsigned)w + j > el && (unsigned)w < el)
    					j = el - w;           /* make EOB code end at table */
    				z = 1 << j;             /* table entries for j-bit table */
    				l[h] = j;               /* set table size in stack */
    
    
    										/* allocate and link in new table */
    				if ((q = (struct huft *)malloc((z + 1) * sizeof(struct huft))) ==
    					(struct huft *)NULL)
    				{
    					if (h)
    						huft_free(u[0]);
    					return 3;             /* not enough memory */
    				}
    				*t = q + 1;             /* link to list for huft_free() */
    				*(t = &(q->v.t)) = (struct huft *)NULL;
    				u[h] = ++q;             /* table starts after link */
    
    
    										/* connect to last table, if there is one */
    				if (h)
    				{
    					x[h] = i;             /* save pattern for backing up */
    					r.b = (uch)l[h - 1];    /* bits to dump before this table */
    					r.e = (uch)(32 + j);  /* bits in this table */
    					r.v.t = q;            /* pointer to this table */
    					j = (i & ((1 << w) - 1)) >> (w - l[h - 1]);
    					u[h - 1][j] = r;        /* connect to last table */
    				}
    			}
    
    
    			/* set up table entry in r */
    			r.b = (uch)(k - w);
    			if (p >= v + n)
    				r.e = INVALID_CODE;     /* out of values--invalid code */
    			else if (*p < s)
    			{
    				r.e = (uch)(*p < 256 ? 32 : 31);  /* 256 is end-of-block code */
    				r.v.n = (ush)*p++;                /* simple code is just the value */
    			}
    			else
    			{
    				r.e = e[*p - s];        /* non-simple--look up in lists */
    				r.v.n = d[*p++ - s];
    			}
    
    
    			/* fill code-like entries with r */
    			f = 1 << (k - w);
    			for (j = i >> w; j < z; j += f)
    				q[j] = r;
    
    
    			/* backwards increment the k-bit code i */
    			for (j = 1 << (k - 1); i & j; j >>= 1)
    				i ^= j;
    			i ^= j;
    
    
    			/* backup over finished tables */
    			while ((i & ((1 << w) - 1)) != x[h])
    				w -= l[--h];            /* don't need to update q */
    		}
    	}
    
    
    
    
    	/* return actual size of base table */
    	*m = l[0];
    
    
    
    
    	/* Return true (1) if we were given an incomplete table */
    	return y != 0 && g != 1;
    }
    
    
    static int inflate_codes(struct huft *tl, struct huft *td, unsigned bl, unsigned bd, Uz_Globs *G)
    {
    	register unsigned e;  /* table entry flag/number of extra bits */
    	unsigned d;           /* index for copy */
    	UINT_D64 n;           /* length for copy (deflate64: might be 64k+2) */
    	UINT_D64 w;           /* current window position (deflate64: up to 64k) */
    	struct huft *t;       /* pointer to table entry */
    	unsigned ml, md;      /* masks for bl and bd bits */
    	register ulg b;       /* bit buffer */
    	register unsigned k;  /* number of bits in bit buffer */
    	int retval = 0;       /* error code returned: initialized to "no error" */
    
    
    
    
    						  /* make local copies of globals */
    	b = G->bb;                       /* initialize bit buffer */
    	k = G->bk;
    	w = G->wp;                       /* initialize window position */
    
    
    	int i = 0;
    									/* inflate the coded data */
    	ml = mask_bits[bl];           /* precompute masks for speed */
    	md = mask_bits[bd];
    	while (1)                     /* do until end of block */
    	{
    		NEEDBITS(bl)
    		t = tl + ((unsigned)b & ml);
    		while (1) {
    			DUMPBITS(t->b)
    
    
    				if ((e = t->e) == 32)     /* then it's a literal */
    				{
    					G->Slide[w++] = (uch)t->v.n;
    					if (w == wsize)
    					{
    						memcpy(G->outptr + G->blockno++ * sizeof(G->Slide), G->Slide, sizeof(G->Slide));
    						memset(G->Slide, 0, sizeof(G->Slide));
    						w = 0;
    					}
    					break;
    				}
    
    
    			if (e < 31)               /* then it's a length */
    			{
    				/* get length of block to copy */
    				NEEDBITS(e)
    					n = t->v.n + ((unsigned)b & mask_bits[e]);
    				DUMPBITS(e)
    
    
    					/* decode distance of block to copy */
    					NEEDBITS(bd)
    					t = td + ((unsigned)b & md);
    				while (1) {
    					DUMPBITS(t->b)
    						if ((e = t->e) < 32)
    							break;
    					if (IS_INVALID_CODE(e))
    						return 1;
    					e &= 31;
    					NEEDBITS(e)
    						t = t->v.t + ((unsigned)b & mask_bits[e]);
    				}
    				NEEDBITS(e)
    					d = (unsigned)w - t->v.n - ((unsigned)b & mask_bits[e]);
    				DUMPBITS(e)
    
    
    					/* do the copy */
    					do {
    						e = (unsigned)(wsize -
    							((d &= (unsigned)(wsize - 1)) > (unsigned)w ? (UINT_D64)d : w));
    						if ((UINT_D64)e > n) e = (unsigned)n;
    						n -= e;
    						if ((unsigned)w - d >= e)
    							/* (this test assumes unsigned comparison) */
    						{
    							memcpy(G->Slide + (unsigned)w, G->Slide + d, e);
    							w += e;
    							d += e;
    						}
    						else                  /* do it slowly to avoid memcpy() overlap */
    							do {
    								G->Slide[w++] = G->Slide[d++];;
    							} while (--e);
    						if (w == wsize)
    						{
    							memcpy(G->outptr + G->blockno * sizeof(G->Slide), G->Slide, sizeof(G->Slide));
    							memset(G->Slide, 0, d);
    							G->blockno = G->blockno + 1;
    							w = 0;	
    						}
    					} while (n);
    					break;
    			}
    
    
    			if (e == 31)              /* it's the EOB signal */
    			{
    				/* sorry for this goto, but we have to exit two loops at once */
    				goto cleanup_decode;
    			}
    
    
    			if (IS_INVALID_CODE(e))
    				return 1;
    
    
    			e &= 31;
    			NEEDBITS(e)
    				t = t->v.t + ((unsigned)b & mask_bits[e]);
    		}
    	}
    cleanup_decode:
    
    
    	/* restore the globals from the locals */
    	G->wp = (unsigned)w;             /* restore global window pointer */
    	G->bb = b;                       /* restore global bit buffer */
    	G->bk = k;
    
    
    cleanup_and_exit:
    	/* done */
    	return retval;
    }
    
    
    static int inflate_dynamic(Uz_Globs *G)
    /* decompress an inflated type 2 (dynamic Huffman codes) block. */
    {
    	unsigned i;           /* temporary variables */
    	unsigned j;
    	unsigned l;           /* last length */
    	unsigned m;           /* mask for bit lengths table */
    	unsigned n;           /* number of lengths to get */
    	struct huft *tl;      /* literal/length code table */
    	struct huft *td;      /* distance code table */
    	unsigned bl;          /* lookup bits for tl */
    	unsigned bd;          /* lookup bits for td */
    	unsigned nb;          /* number of bit length codes */
    	unsigned nl;          /* number of literal/length codes */
    	unsigned nd;          /* number of distance codes */
    	unsigned ll[MAXLITLENS + MAXDISTS]; /* lit./length and distance code lengths */
    	register ulg b;       /* bit buffer */
    	register unsigned k;  /* number of bits in bit buffer */
    	int retval = 0;       /* error code returned: initialized to "no error" */
    
    
    
    
    						  /* make local bit buffer */
    	b = G->bb;
    	k = G->bk;
    
    
    
    
    	/* read in table lengths */
    	NEEDBITS(5)
    		nl = 257 + ((unsigned)b & 0x1f);      /* number of literal/length codes */
    	DUMPBITS(5)
    		NEEDBITS(5)
    		nd = 1 + ((unsigned)b & 0x1f);        /* number of distance codes */
    	DUMPBITS(5)
    		NEEDBITS(4)
    		nb = 4 + ((unsigned)b & 0xf);         /* number of bit length codes */
    	DUMPBITS(4)
    		if (nl > MAXLITLENS || nd > MAXDISTS)
    			return 1;                   /* bad lengths */
    
    
    
    
    										/* read in bit-length-code lengths */
    	for (j = 0; j < nb; j++)
    	{
    		NEEDBITS(3)
    			ll[border[j]] = (unsigned)b & 7;
    		DUMPBITS(3)
    	}
    	for (; j < 19; j++)
    		ll[border[j]] = 0;
    
    
    
    
    	/* build decoding table for trees--single level, 7 bit lookup */
    	bl = 7;
    	retval = huft_build(ll, 19, 19, NULL, NULL, &tl, &bl);
    	if (bl == 0)                  /* no bit lengths */
    		retval = 1;
    	if (retval)
    	{
    		if (retval == 1)
    			huft_free(tl);
    		return retval;              /* incomplete code set */
    	}
    
    
    
    
    	/* read in literal and distance code lengths */
    	n = nl + nd;
    	m = mask_bits[bl];
    	i = l = 0;
    	while (i < n)
    	{
    		NEEDBITS(bl)
    			j = (td = tl + ((unsigned)b & m))->b;
    		DUMPBITS(j)
    			j = td->v.n;
    		if (j < 16)                 /* length of code in bits (0..15) */
    			ll[i++] = l = j;          /* save last length in l */
    		else if (j == 16)           /* repeat last length 3 to 6 times */
    		{
    			NEEDBITS(2)
    				j = 3 + ((unsigned)b & 3);
    			DUMPBITS(2)
    				if ((unsigned)i + j > n)
    					return 1;
    			while (j--)
    				ll[i++] = l;
    		}
    		else if (j == 17)           /* 3 to 10 zero length codes */
    		{
    			NEEDBITS(3)
    				j = 3 + ((unsigned)b & 7);
    			DUMPBITS(3)
    				if ((unsigned)i + j > n)
    					return 1;
    			while (j--)
    				ll[i++] = 0;
    			l = 0;
    		}
    		else                        /* j == 18: 11 to 138 zero length codes */
    		{
    			NEEDBITS(7)
    				j = 11 + ((unsigned)b & 0x7f);
    			DUMPBITS(7)
    				if ((unsigned)i + j > n)
    					return 1;
    			while (j--)
    				ll[i++] = 0;
    			l = 0;
    		}
    	}
    
    
    
    
    	/* free decoding table for trees */
    	huft_free(tl);
    
    
    
    
    	/* restore the global bit buffer */
    	G->bb = b;
    	G->bk = k;
    
    
    
    
    	/* build the decoding tables for literal/length and distance codes */
    	bl = lbits;
    	retval = huft_build(ll, nl, 257, G->cplens, G->cplext, &tl, &bl);
    	if (bl == 0)                  /* no literals or lengths */
    		retval = 1;
    	if (retval)
    	{
    		if (retval == 1) {
    			huft_free(tl);
    		}
    		return retval;              /* incomplete code set */
    	}
    
    
    	bd = dbits;
    
    
    
    
    	retval = huft_build(ll + nl, nd, 0, cpdist, G->cpdext, &td, &bd);
    
    
    	if (retval == 1)
    		retval = 0;
    	if (bd == 0 && nl > 257)    /* lengths but no distances */
    		retval = 1;
    	if (retval)
    	{
    		if (retval == 1) {
    			huft_free(td);
    		}
    		huft_free(tl);
    		return retval;
    	}
    
    
    	/* decompress until an end-of-block code */
    	retval = inflate_codes(tl, td, bl, bd, G);
    
    
    cleanup_and_exit:
    	/* free the decoding tables, return */
    	huft_free(tl);
    	huft_free(td);
    	return retval;
    }
    
    
    static int inflate_stored(Uz_Globs *G)
    {
    	UINT_D64 w;           /* current window position (deflate64: up to 64k!) */
    	unsigned n;           /* number of bytes in block */
    	register ulg b;       /* bit buffer */
    	register unsigned k;  /* number of bits in bit buffer */
    	int retval = 0;       /* error code returned: initialized to "no error" */
    
    
    	b = G->bb;                       /* initialize bit buffer */
    	k = G->bk;
    	w = G->wp;                       /* initialize window position */
    
    
    
    
    									/* go to byte boundary */
    	n = k & 7;
    	DUMPBITS(n);
    
    
    
    
    	/* get the length and its complement */
    	NEEDBITS(16)
    		n = ((unsigned)b & 0xffff);
    	DUMPBITS(16)
    		NEEDBITS(16)
    		if (n != (unsigned)((~b) & 0xffff))
    			return 1;                   /* error in compressed data */
    	DUMPBITS(16)
    
    
    
    
    		/* read and output the compressed data */
    		while (n--)
    		{
    			NEEDBITS(8)
    				G->Slide[w++] = (uch)b;
    			if (w == wsize)
    			{
    				memcpy(G->outptr + G->blockno++ * sizeof(G->Slide), G->Slide, sizeof(G->Slide));
    				memset(G->Slide, 0, sizeof(G->Slide));
    				w = 0;
    			}
    			DUMPBITS(8)
    		}
    
    
    	/* restore the globals from the locals */
    	G->wp = (unsigned)w;             /* restore global window pointer */
    	G->bb = b;                       /* restore global bit buffer */
    	G->bk = k;
    
    
    cleanup_and_exit:
    	return retval;
    }
    
    
    static int inflate_fixed(Uz_Globs *G)
    {
    	if (G->fixed_tl == (struct huft *)NULL)
    	{
    		int i;                /* temporary variable */
    		unsigned l[288];      /* length list for huft_build */
    
    
    							  /* literal table */
    		for (i = 0; i < 144; i++)
    			l[i] = 8;
    		for (; i < 256; i++)
    			l[i] = 9;
    		for (; i < 280; i++)
    			l[i] = 7;
    		for (; i < 288; i++)          /* make a complete, but wrong code set */
    			l[i] = 8;
    		G->fixed_bl = 7;
    
    
    		if ((i = huft_build(l, 288, 257, G->cplens, G->cplext,
    			&G->fixed_tl, &G->fixed_bl)) != 0)
    		{
    			G->fixed_tl = (struct huft *)NULL;
    			return i;
    		}
    
    
    		/* distance table */
    		for (i = 0; i < MAXDISTS; i++)      /* make an incomplete code set */
    			l[i] = 5;
    		G->fixed_bd = 5;
    
    
    		if ((i = huft_build(l, MAXDISTS, 0, cpdist, G->cpdext,
    			&G->fixed_td, &G->fixed_bd)) > 1)
    		{
    			huft_free(G->fixed_tl);
    			G->fixed_td = G->fixed_tl = (struct huft *)NULL;
    			return i;
    		}
    	}
    
    
    	/* decompress until an end-of-block code */
    	return inflate_codes(G->fixed_tl, G->fixed_td,
    		G->fixed_bl, G->fixed_bd, G);
    }
    
    
    static int inflate_block(int *e, Uz_Globs *G)
    {
    	unsigned t;           /* block type */
    	register ulg b;       /* bit buffer */
    	register unsigned k;  /* number of bits in bit buffer */
    	int retval = 0;       /* error code returned: initialized to "no error" */
    
    
    
    
    						  /* make local bit buffer */
    	b = G->bb;
    	k = G->bk;
    
    
    
    
    	/* read in last block bit */
    	NEEDBITS(1)
    		*e = (int)b & 1;
    	DUMPBITS(1)
    
    
    
    
    		/* read in block type */
    		NEEDBITS(2)
    		t = (unsigned)b & 3;
    	DUMPBITS(2)
    
    
    
    
    		/* restore the global bit buffer */
    		G->bb = b;
    	G->bk = k;
    
    
    
    
    	/* inflate that block type */
    	if (t == 2)
    		return inflate_dynamic(G);
    	if (t == 0)
    		return inflate_stored(G);
    	if (t == 1)
    		return inflate_fixed(G);
    
    
    
    
    	/* bad block type */
    	retval = 2;
    
    
    cleanup_and_exit:
    	return retval;
    }
    
    
    int MZUnzip(uint8_t *unzip, uint8_t *data, uint32_t zip_size)
    {
    	Uz_Globs G;
    	init_global_variables(&G);
    
    
    	G.inptr = data;
    	G.outptr = unzip;
    	G.incnt = zip_size;
    
    
    	G.cplens = cplens32;
    	G.cplext = cplext32;
    	G.cpdext = cpdext32;
    	G.fixed_tl = G.fixed_tl32;
    	G.fixed_bl = G.fixed_bl32;
    	G.fixed_td = G.fixed_td32;
    	G.fixed_bd = G.fixed_bd32;
    
    
    	int r = 0, e = 0;
    	do {
    		if ((r = inflate_block(&e, &G)) != 0)
    		{
    			return r;
    		}
    	} while (!e);
    
    
    	G.fixed_tl32 = G.fixed_tl;
    	G.fixed_bl32 = G.fixed_bl;
    	G.fixed_td32 = G.fixed_td;
    	G.fixed_bd32 = G.fixed_bd;
    	memcpy(unzip + G.blockno * sizeof(G.Slide), G.Slide, G.wp);
    
    
    	return r;
    }
    
    
    int MZUnzipFile(const char *src)
    {
    	const char *zipfilename;
    	int zipfilefd;
    	int zipfilelen;
    	unsigned char *zipfilebuff;
    	struct stat stat_zipfile;
    
    
    	ssize_t readret, writeret;
    	int filezipsize = 0;
    	int fileunzipsize = 0;
    	int filenamelen = 0;
    	int fileextralen = 0;
    	int filezipflag = 0;
    	int filedescriptor = 0;
    	int filezipheadsize = 0;
    	char *filename;
    	char *filebuff;
    	char *fileunbuff;
    
    
    	memset(&stat_zipfile, 0, sizeof(stat_zipfile));
    
    
    	zipfilename = src;
    	stat(zipfilename, &(stat_zipfile));
    	zipfilelen = stat_zipfile.st_size;
    
    
    	zipfilebuff = malloc(zipfilelen);
    	if (!zipfilebuff)
    		return 1;
    	memset(zipfilebuff, 0, zipfilelen);
    
    
    	zipfilefd = open(zipfilename, O_RDONLY | O_BINARY);
    	while ((readret = read(zipfilefd, zipfilebuff, zipfilelen)))
    	{
    		if (readret < 0)
    			break;
    	}
    	close(zipfilefd);
    
    
    	memcpy(&filezipsize, zipfilebuff + 18, 4);
    	memcpy(&fileunzipsize, zipfilebuff + 22, 4);
    	memcpy(&filenamelen, zipfilebuff + 26, 2);
    	memcpy(&fileextralen, zipfilebuff + 28, 2);
    	filezipheadsize = 30 + filenamelen + fileextralen;
    
    
    	//做个简单的文件校验，具体内容请查阅zip文件格式
    	//文件头+压缩后的大小不等于固定值0x02014b50，则说明文件不完整
    	//file_zipflag的第三比特位为1，则在数据段后面会有一个固定值为0x08074b50的Data descriptor结构
    	memcpy(&filedescriptor, zipfilebuff + filezipheadsize + filezipsize, 4);
    	if (filezipflag & 0x08 == 0x08)
    	{
    		if (filedescriptor != 0x08074b50)
    		{
    			return -1;
    		}
    	}
    	else
    	{
    		if (filedescriptor != 0x02014b50)
    		{
    			return -1;
    		}
    	}
    
    
    	filename = malloc(filenamelen);
    	filebuff = malloc(filezipsize);
    	fileunbuff = malloc(fileunzipsize);
    
    
    	if (!filename || !filebuff || !fileunzipsize)
    		return -1;
    
    
    	memset(filename, 0, filenamelen);
    	memset(filebuff, 0, filezipsize);
    	memset(fileunbuff, 0, fileunzipsize);
    
    
    	memcpy(filename, zipfilebuff + 30, filenamelen);
    	memcpy(filebuff, zipfilebuff + filezipheadsize, filezipsize);
    
    
    	free(zipfilebuff);
    	zipfilebuff = NULL;
    
    
    	int r = MZUnzip(fileunbuff, filebuff, filezipsize);
    	if (r)
    		return r;
    
    
    	int outfile = open(filename, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    	if (outfile < 0)
    	{
    		r = -1;
    		goto END;
    	}
    
    
    	int pos = 0;
    	writeret = 0;
    
    
    	while (1)
    	{
    		writeret = write(outfile, fileunbuff + pos, (fileunzipsize - pos > 1024 ? 1024 : fileunzipsize - pos));
    		pos += writeret;
    
    
    		if (writeret < 0)
    			break;
    
    
    		if (pos == fileunzipsize)
    			break;
    	}
    
    
    	close(outfile);
    
    
    END:
    	free(filename);
    	free(filebuff);
    	free(fileunbuff);
    	filename = NULL;
    	filebuff = NULL;
    	fileunbuff = NULL;
    	return 0;
    }
    
    
    #if 0
    int main(int argc, char **argv)
    {
    	int r = MZUnzipFile("/home/zhangn/work/myunzip/bin/x64/Debug/1.zip");
    	return r;
    }
    #endif

