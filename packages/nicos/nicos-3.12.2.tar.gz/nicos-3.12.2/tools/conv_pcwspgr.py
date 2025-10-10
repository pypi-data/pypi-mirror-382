sg_by_num = {}
sg_by_hm  = {}

with open('PCWSPGR.DAT', encoding='utf-8') as f:  # from PowderCell
    for line in f:
        if line.startswith('spgr'):
            sp = line.split(None, 8)
            spnum = int(sp[1])
            spvar = int(sp[2])
            hm = sp[8].strip()

            sp_hm = hm.replace(' ', '')
            sp_cond = next(f)
            conditions = [int(sp_cond[2*i:2*i+2]) for i in range(14)]
            if sp_hm in sg_by_hm:
                if sp_hm not in ('R3', 'R-3', 'R32', 'R3m', 'R3c',
                                 'R-32m', 'R-32/m', 'R-32/c'):
                    assert sg_by_num[sg_by_hm[sp_hm]] == conditions, sp_hm
            else:
                sg_by_hm[sp_hm] = spnum, spvar
            sg_by_num[spnum, spvar] = conditions

with open('nph-list_table', encoding='utf-8') as g:  # from www.cryst.ehu.es
    for line in g:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('231'):
            continue
        nr, hm = line.split()
        nr = int(nr)
        if hm in sg_by_hm:
            assert sg_by_hm[hm][0] == nr
        else:
            sg_by_hm[hm] = (nr, 1)

print('sg_by_num = {')
for k in sorted(sg_by_num):
    print('   %-9s: %s,' % (k, sg_by_num[k]))
print('}\n')
print('sg_by_hm = {')
for k in sorted(sg_by_hm):
    print('   %-9r: %s,' % (k, sg_by_hm[k]))
print('}')
