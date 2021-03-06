import collections
import types
from functools import reduce

from ..core.data import WARP
from .syntax import reTp

# LOW-LEVEL NODE RELATIONS SEMANTICS ###


def basicRelations(searchExe, api, silent):
  C = api.C
  F = api.F
  E = api.E
  info = api.info
  msgCache = searchExe.msgCache
  Crank = C.rank.data
  ClevDown = C.levDown.data
  ClevUp = C.levUp.data
  (CfirstSlots, ClastSlots) = C.boundary.data
  Eoslots = E.oslots.data
  slotType = F.otype.slotType
  maxSlot = F.otype.maxSlot
  sets = searchExe.sets
  setInfo = searchExe.setInfo

  def isSlotType(nType):
    if sets is not None and nType in sets:
      if nType in setInfo:
        return setInfo[nType]
      nodes = sets[nType]
      allSlots = all(n <= maxSlot for n in nodes)
      if allSlots:
        setInfo[nType] = True
        return True
      allNonSlots = all(n > maxSlot for n in nodes)
      if allNonSlots:
        setInfo[nType] = False
        return False
      setInfo[nType] = None
      return None
    return nType == slotType

  # EQUAL

  def equalR(fTp, tTp):
    return lambda n: (n, )

  def spinEqual(fTp, tTp):

    def doyarns(yF, yT):
      x = set(yF) & set(yT)
      return (x, x)

    return doyarns

  # UNEQUAL

  def unequalR(fTp, tTp):
    return lambda n, m: n != m

  # CANONICAL BEFORE

  def canonicalBeforeR(fTp, tTp):
    return lambda n, m: Crank[n - 1] < Crank[m - 1]

  # CANONICAL AFTER

  def canonicalAfterR(fTp, tTp):
    return lambda n, m: Crank[n - 1] > Crank[m - 1]

  # SAME SLOTS

  def spinSameSlots(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:

      def doyarns(yF, yT):
        x = set(yF) & set(yT)
        return (x, x)

      return doyarns

    elif isSlotF or isSlotT:

      def doyarns(yS, y2):
        sindex = {}
        for m in y2:
          ss = Eoslots[m - maxSlot - 1] if m > maxSlot else (m, )
          if len(ss) == 1:
            sindex.setdefault(ss[0], set()).add(m)
        nyS = yS & set(sindex.keys())
        ny2 = reduce(
            set.union,
            (sindex[s] for s in nyS),
            set(),
        )
        return (nyS, ny2)

      if isSlotF:
        return doyarns

      else:

        def xx(yF, yT):
          (nyT, nyF) = doyarns(yT, yF)
          return (nyF, nyT)

        return xx

    else:

      def doyarns(yF, yT):
        sindexF = {}
        for n in yF:
          s = frozenset(Eoslots[n - maxSlot - 1] if n > maxSlot else (n, ))
          sindexF.setdefault(s, set()).add(n)
        sindexT = {}
        for m in yT:
          s = frozenset(Eoslots[m - maxSlot - 1] if m > maxSlot else (m, ))
          sindexT.setdefault(s, set()).add(m)
        nyS = set(sindexF.keys()) & set(sindexT.keys())
        nyF = reduce(
            set.union,
            (sindexF[s] for s in nyS),
            set(),
        )
        nyT = reduce(
            set.union,
            (sindexT[s] for s in nyS),
            set(),
        )
        return (nyF, nyT)

      return doyarns

  def sameSlotsR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n: (n, )
    elif isSlotT:
      return lambda n, m: ((Eoslots[n - maxSlot - 1] if n > maxSlot else (n, )) == (m, ))
    elif isSlotF:
      return lambda n, m: ((Eoslots[m - maxSlot - 1] if m > maxSlot else (m, )) == (n, ))
    else:
      return (
          lambda n, m: ((n <= maxSlot and m == n) or (
              frozenset(Eoslots[n - maxSlot - 1] if n > maxSlot else (n, )) ==
              frozenset(Eoslots[m - maxSlot - 1] if m > maxSlot else (m, ))
          ))
      )

  # OVERLAP

  def spinOverlap(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:

      def doyarns(yF, yT):
        x = set(yF) & set(yT)
        return (x, x)

      return doyarns
    elif isSlotF or isSlotT:

      def doyarns(yS, y2):
        sindex = {}
        for m in y2:
          for s in Eoslots[m - maxSlot - 1] if m > maxSlot else (m, ):
            sindex.setdefault(s, set()).add(m)
        nyS = yS & set(sindex.keys())
        ny2 = reduce(
            set.union,
            (sindex[s] for s in nyS),
            set(),
        )
        return (nyS, ny2)

      if isSlotF:
        return doyarns
      else:

        def xx(yF, yT):
          (nyT, nyF) = doyarns(yT, yF)
          return (nyF, nyT)

        return xx
    else:

      def doyarns(yF, yT):
        REDUCE_FACTOR = 0.4
        SIZE_LIMIT = 10000
        sindexF = {}
        for n in yF:
          for s in Eoslots[n - maxSlot - 1] if n > maxSlot else (n, ):
            sindexF.setdefault(s, set()).add(n)
        sindexT = {}
        for m in yT:
          for s in Eoslots[m - maxSlot - 1] if m > maxSlot else (m, ):
            sindexT.setdefault(s, set()).add(m)
        nyS = set(sindexF.keys()) & set(sindexT.keys())

        lsF = len(sindexF)
        lsT = len(sindexT)
        lsI = len(nyS)
        if lsF == lsT:  # spinning is completely useless
          return (yF, yT)
        if lsI > REDUCE_FACTOR * lsT and lsT > SIZE_LIMIT:
          # spinning is not worth it
          return (yF, yT)

        if not silent:
          info(f'1. reducing over {len(nyS)} elements', cache=msgCache)
        nyF = reduce(
            set.union,
            (sindexF[s] for s in nyS),
            set(),
        )
        if not silent:
          info(f'2. reducing over {len(nyS)} elements', cache=msgCache)
        nyT = reduce(
            set.union,
            (sindexT[s] for s in nyS),
            set(),
        )
        return (nyF, nyT)

      return doyarns

  def overlapR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n: (n, )
    elif isSlotT:
      return lambda n: (Eoslots[n - maxSlot - 1] if n > maxSlot else (n, ))
    elif isSlotF:
      return lambda n, m: (n in frozenset(Eoslots[m - maxSlot - 1] if m > maxSlot else (m, )))
    else:
      return (
          lambda n, m: (
              len(
                  frozenset(Eoslots[n - maxSlot - 1] if n > maxSlot else (n, ))
                  & frozenset(Eoslots[m - maxSlot - 1] if m > maxSlot else (m, ))
              ) != 0
          )
      )

  # DIFFERENT SLOTS

  def diffSlotsR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n, m: m != n
    elif isSlotT:
      return lambda n, m: ((Eoslots[m - maxSlot - 1] if m > maxSlot else (m, )) != (n, ))
    elif isSlotF:
      return lambda n, m: ((Eoslots[n - maxSlot - 1] if n > maxSlot else (n, )) != (m, ))
    else:
      return (
          lambda n, m: (
              frozenset(Eoslots[n - maxSlot - 1] if n > maxSlot else (n, )) !=
              frozenset(Eoslots[m - maxSlot - 1] if m > maxSlot else (m, ))
          )
      )

  # DISJOINT SLOTS

  def disjointSlotsR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n, m: m != n
    elif isSlotT:
      return lambda n, m: m not in frozenset(Eoslots[n - maxSlot - 1] if n > maxSlot else (n, ))
    elif isSlotF:
      return lambda n, m: n not in frozenset(Eoslots[m - maxSlot - 1] if m > maxSlot else (m, ))
    else:
      return (
          lambda n, m: (
              len(
                  frozenset(Eoslots[n - maxSlot - 1] if n > maxSlot else (n, ))
                  & frozenset(Eoslots[m - maxSlot - 1] if m > maxSlot else (m, ))
              ) == 0
          )
      )

  # EMBEDDED IN

  def inR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n: ()
    elif isSlotT:
      return lambda n: ()
    elif isSlotF:
      return lambda n: ClevUp[n - 1]
    else:
      return lambda n: ClevUp[n - 1]

  # EMBEDS

  def hasR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n: ()
    elif isSlotF:
      return lambda n: ()
    elif isSlotT:
      return lambda n: Eoslots[n - maxSlot - 1] if n > maxSlot else ()
    else:
      if isSlotT is None:
        return lambda n: ((ClevDown[n - maxSlot - 1] + Eoslots[n - maxSlot - 1])
                          if n > maxSlot else ())
      else:
        return lambda n: (ClevDown[n - maxSlot - 1] if n > maxSlot else ())

  # BEFORE WRT SLOTS

  def slotBeforeR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n, m: n < m
    elif isSlotF:
      return lambda n, m: n < (Eoslots[m - maxSlot - 1][0] if m > maxSlot else m)
    elif isSlotT:
      return lambda n, m: (Eoslots[n - maxSlot - 1][-1] if n > maxSlot else n) < m
    else:
      return lambda n, m: ((Eoslots[n - maxSlot - 1][-1] if n > maxSlot else n) <
                           (Eoslots[m - maxSlot - 1][0] if m > maxSlot else m))

  # AFTER WRT SLOTS

  def slotAfterR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n, m: n > m
    elif isSlotF:
      return lambda n, m: n > (Eoslots[m - maxSlot - 1][-1] if m > maxSlot else m)
    elif isSlotT:
      return lambda n, m: (Eoslots[n - maxSlot - 1][0] if n > maxSlot else n) > m
    else:
      return lambda n, m: ((Eoslots[n - maxSlot - 1][0] if n > maxSlot else n) >
                           (Eoslots[m - maxSlot - 1][-1] if m > maxSlot else m))

  # START AT SAME SLOT

  def sameFirstSlotR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n: (n, )
    elif isSlotF:
      if isSlotT is None:
        return lambda n: CfirstSlots[n - 1] + (n, )
      else:
        return lambda n: CfirstSlots[n - 1]
    elif isSlotT:
      return lambda n: ((Eoslots[n - maxSlot - 1][0] if n > maxSlot else n), )
    else:

      def xx(n):
        fn = Eoslots[n - maxSlot - 1][0] if n > maxSlot else n
        if isSlotT is None:
          return CfirstSlots[fn - 1] + (fn, )
        else:
          return CfirstSlots[fn - 1]

      return xx

  # ENDS AT SAME SLOT

  def sameLastSlotR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n: (n, )
    elif isSlotF:
      if isSlotT is None:
        return lambda n: ClastSlots[n - 1] + (n, )
      else:
        return lambda n: ClastSlots[n - 1]
    elif isSlotT:
      return lambda n: ((Eoslots[n - maxSlot - 1][-1] if n > maxSlot else n), )
    else:

      def xx(n):
        ln = Eoslots[n - maxSlot - 1][-1] if n > maxSlot else n
        if isSlotT is None:
          return ClastSlots[ln - 1] + (ln, )
        else:
          return ClastSlots[ln - 1]

      return xx

  # START AND END AT SAME SLOT

  def sameBoundaryR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n: (n, )
    elif isSlotF:
      if isSlotT is None:

        def xx(n):
          fok = set(CfirstSlots[n - 1] + (n, ))
          lok = set(ClastSlots[n - 1] + (n, ))
          return tuple(fok & lok)

      else:

        def xx(n):
          fok = set(CfirstSlots[n - 1])
          lok = set(ClastSlots[n - 1])
          return tuple(fok & lok)

      return xx
    elif isSlotT:

      def xx(n):
        slots = Eoslots[n - maxSlot - 1] if n > maxSlot else (n, )
        fs = slots[0]
        ls = slots[-1]
        return (fs, ) if fs == ls else ()

      return xx
    else:
      if isSlotT is None:

        def xx(n):
          fn = Eoslots[n - maxSlot - 1][0] if n > maxSlot else n
          ln = Eoslots[n - maxSlot - 1][-1] if n > maxSlot else n
          fok = set(CfirstSlots[fn - 1] + (fn, ))
          lok = set(ClastSlots[ln - 1] + (ln, ))
          return tuple(fok & lok)

      else:

        def xx(n):
          fn = Eoslots[n - maxSlot - 1][0] if n > maxSlot else n
          ln = Eoslots[n - maxSlot - 1][-1] if n > maxSlot else n
          fok = set(CfirstSlots[fn - 1])
          lok = set(ClastSlots[ln - 1])
          return tuple(fok & lok)

      return xx

  # FIRST SLOTS ARE k-CLOSE

  def nearFirstSlotR(k):

    def zz(fTp, tTp):
      isSlotF = isSlotType(fTp)
      isSlotT = isSlotType(tTp)
      if isSlotF and isSlotT:
        return lambda n: tuple(m for m in range(max((1, n - k)), min((maxSlot, n + k)) + 1))
      elif isSlotF:
        if isSlotT is None:

          def xx(n):
            near = set(l for l in range(max((1, n - k)), min((maxSlot, n + k)) + 1))
            return tuple(
                reduce(
                    set.union,
                    (set(CfirstSlots[l - 1] + (l, )) for l in near),
                    set(),
                )
            )
        else:

          def xx(n):
            near = set(l for l in range(max((1, n - k)), min((maxSlot, n + k)) + 1))
            return tuple(reduce(
                set.union,
                (set(CfirstSlots[l - 1]) for l in near),
                set(),
            ))

        return xx
      elif isSlotT:

        def xx(n):
          fn = Eoslots[n - maxSlot - 1][0] if n > maxSlot else n
          return tuple(m for m in range(max((1, fn - k)), min((maxSlot, fn + k)) + 1))

        return xx

      else:
        if isSlotT is None:

          def xx(n):
            fn = Eoslots[n - maxSlot - 1][0] if n > maxSlot else n
            near = set(l for l in range(max((1, fn - k)), min((maxSlot, fn + k)) + 1))
            return tuple(
                reduce(
                    set.union,
                    (set(CfirstSlots[l - 1] + (l, )) for l in near),
                    set(),
                )
            )

        else:

          def xx(n):
            fn = Eoslots[n - maxSlot - 1][0] if n > maxSlot else n
            near = set(l for l in range(max((1, fn - k)), min((maxSlot, fn + k)) + 1))
            return tuple(reduce(
                set.union,
                (set(CfirstSlots[l - 1]) for l in near),
                set(),
            ))

        return xx

    return zz

  # LAST SLOTS ARE k-CLOSE

  def nearLastSlotR(k):

    def zz(fTp, tTp):
      isSlotF = isSlotType(fTp)
      isSlotT = isSlotType(tTp)
      if isSlotF and isSlotT:
        return lambda n: tuple(m for m in range(max((1, n - k)), min((maxSlot, n + k)) + 1))
      elif isSlotF:
        if isSlotT is None:

          def xx(n):
            near = set(l for l in range(max((1, n - k)), min((maxSlot, n + k)) + 1))
            return tuple(
                reduce(
                    set.union,
                    (set(ClastSlots[l - 1] + (l, )) for l in near),
                    set(),
                )
            )

        else:

          def xx(n):
            near = set(l for l in range(max((1, n - k)), min((maxSlot, n + k)) + 1))
            return tuple(reduce(
                set.union,
                (set(ClastSlots[l - 1]) for l in near),
                set(),
            ))

        return xx
      elif isSlotT:

        def xx(n):
          ln = Eoslots[n - maxSlot - 1][-1] if n > maxSlot else n
          return tuple(m for m in range(max((1, ln - k)), min((maxSlot, ln + k)) + 1))

        return xx
      else:
        if isSlotT is None:

          def xx(n):
            ln = Eoslots[n - maxSlot - 1][-1] if n > maxSlot else n
            near = set(l for l in range(max((1, ln - k)), min((maxSlot, ln + k)) + 1))
            return tuple(
                reduce(
                    set.union,
                    (set(ClastSlots[l - 1] + (l, )) for l in near),
                    set(),
                )
            )

        else:

          def xx(n):
            ln = Eoslots[n - maxSlot - 1][-1] if n > maxSlot else n
            near = set(l for l in range(max((1, ln - k)), min((maxSlot, ln + k)) + 1))
            return tuple(reduce(
                set.union,
                (set(ClastSlots[l - 1]) for l in near),
                set(),
            ))

        return xx

    return zz

  # FIRST SLOTS ARE k-CLOSE and LAST SLOTS ARE k-CLOSE

  def nearBoundaryR(k):

    def zz(fTp, tTp):
      isSlotF = isSlotType(fTp)
      isSlotT = isSlotType(tTp)
      if isSlotF and isSlotT:
        return lambda n: tuple(m for m in range(max((1, n - k)), min((maxSlot, n + k)) + 1))
      elif isSlotF:
        if isSlotT is None:

          def xx(n):
            near = set(l for l in range(max((1, n - k)), min((maxSlot, n + k)) + 1))
            fok = set(reduce(
                set.union,
                (set(CfirstSlots[l - 1] + (l, )) for l in near),
                set(),
            ))
            lok = set(reduce(
                set.union,
                (set(ClastSlots[l - 1] + (l, )) for l in near),
                set(),
            ))
            return tuple(fok & lok)

        else:

          def xx(n):
            near = set(l for l in range(max((1, n - k)), min((maxSlot, n + k)) + 1))
            fok = set(reduce(
                set.union,
                (set(CfirstSlots[l - 1]) for l in near),
                set(),
            ))
            lok = set(reduce(
                set.union,
                (set(ClastSlots[l - 1]) for l in near),
                set(),
            ))
            return tuple(fok & lok)

        return xx
      elif isSlotT:

        def xx(n):
          slots = Eoslots[n - maxSlot - 1] if n > maxSlot else (n, )
          fs = slots[0]
          ls = slots[-1]
          fok = set(m for m in range(max((1, fs - k)), min((maxSlot, fs + k)) + 1))
          lok = set(m for m in range(max((1, ls - k)), min((maxSlot, ls + k)) + 1))
          return tuple(fok & lok)

        return xx
      else:
        if isSlotT is None:

          def xx(n):
            fn = Eoslots[n - maxSlot - 1][0] if n > maxSlot else n
            ln = Eoslots[n - maxSlot - 1][-1] if n > maxSlot else n
            nearf = set(l for l in range(max((1, fn - k)), min((maxSlot, fn + k)) + 1))
            nearl = set(l for l in range(max((1, ln - k)), min((maxSlot, ln + k)) + 1))
            fok = set(reduce(
                set.union,
                (set(CfirstSlots[l - 1] + (l, )) for l in nearf),
                set(),
            ))
            lok = set(reduce(
                set.union,
                (set(ClastSlots[l - 1] + (l, )) for l in nearl),
                set(),
            ))
            return tuple(fok & lok)

        else:

          def xx(n):
            fn = Eoslots[n - maxSlot - 1][0] if n > maxSlot else n
            ln = Eoslots[n - maxSlot - 1][-1] if n > maxSlot else n
            nearf = set(l for l in range(max((1, fn - k)), min((maxSlot, fn + k)) + 1))
            nearl = set(l for l in range(max((1, ln - k)), min((maxSlot, ln + k)) + 1))
            fok = set(reduce(
                set.union,
                (set(CfirstSlots[l - 1]) for l in nearf),
                set(),
            ))
            lok = set(reduce(
                set.union,
                (set(ClastSlots[l - 1]) for l in nearl),
                set(),
            ))
            return tuple(fok & lok)

        return xx

    return zz

  # FIRST ENDS WHERE SECOND STARTS

  def adjBeforeR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n: (n + 1, ) if n < maxSlot else ()
    else:
      if isSlotT:

        def xx(n):
          if n == maxSlot:
            return ()
          myNext = n + 1 if n < maxSlot else Eoslots[n - maxSlot - 1][-1] + 1
          if myNext > maxSlot:
            return ()
          return (myNext, )

      elif isSlotT is None:

        def xx(n):
          if n == maxSlot:
            return ()
          myNext = n + 1 if n < maxSlot else Eoslots[n - maxSlot - 1][-1] + 1
          if myNext > maxSlot:
            return ()
          return CfirstSlots[myNext - 1] + (myNext, )

      else:

        def xx(n):
          if n == maxSlot:
            return ()
          myNext = n + 1 if n < maxSlot else Eoslots[n - maxSlot - 1][-1] + 1
          if myNext > maxSlot:
            return ()
          return CfirstSlots[myNext - 1]

      return xx

  # FIRST STARTS WHERE SECOND ENDS

  def adjAfterR(fTp, tTp):
    isSlotF = isSlotType(fTp)
    isSlotT = isSlotType(tTp)
    if isSlotF and isSlotT:
      return lambda n: (n - 1, ) if n > 1 else ()
    else:

      if isSlotT:

        def xx(n):
          if n <= 1:
            return ()
          myPrev = n - 1 if n < maxSlot else Eoslots[n - maxSlot - 1][0] - 1
          if myPrev <= 1:
            return ()
          return (myPrev, )

      elif isSlotT is None:

        def xx(n):
          if n <= 1:
            return ()
          myPrev = n - 1 if n < maxSlot else Eoslots[n - maxSlot - 1][0] - 1
          if myPrev <= 1:
            return ()
          return (myPrev, ) + ClastSlots[myPrev - 1]

      else:

        def xx(n):
          if n <= 1:
            return ()
          myPrev = n - 1 if n < maxSlot else Eoslots[n - maxSlot - 1][0] - 1
          if myPrev <= 1:
            return ()
          return ClastSlots[myPrev - 1]

      return xx

  # FIRST ENDS WHERE SECOND STARTS WITHIN k-SLOTS

  def nearBeforeR(k):

    def zz(fTp, tTp):
      isSlotF = isSlotType(fTp)
      isSlotT = isSlotType(tTp)
      if isSlotF and isSlotT:
        return lambda n: tuple(m for m in range(max((1, n + 1 - k)), min((maxSlot, n + 1 + k)) + 1))
      else:
        if isSlotT:

          def xx(n):
            myNext = n + 1 if n < maxSlot else Eoslots[n - maxSlot - 1][-1] + 1
            myNextNear = tuple(
                ls for ls in range(max((1, myNext - k)),
                                   min((maxSlot, myNext + k)) + 1)
            )
            return myNextNear

        elif isSlotT is None:

          def xx(n):
            myNext = n + 1 if n < maxSlot else Eoslots[n - maxSlot - 1][-1] + 1
            myNextNear = tuple(
                ls for ls in range(max((1, myNext - k)),
                                   min((maxSlot, myNext + k)) + 1)
            )
            nextSet = set(
                reduce(
                    set.union,
                    (set(CfirstSlots[ls - 1]) for ls in myNextNear),
                    set(),
                )
            )
            return tuple(nextSet) + myNextNear

        else:

          def xx(n):
            myNext = n + 1 if n < maxSlot else Eoslots[n - maxSlot - 1][-1] + 1
            myNextNear = tuple(
                ls for ls in range(max((1, myNext - k)),
                                   min((maxSlot, myNext + k)) + 1)
            )
            nextSet = set(
                reduce(
                    set.union,
                    (set(CfirstSlots[ls - 1]) for ls in myNextNear),
                    set(),
                )
            )
            return tuple(nextSet)

        return xx

    return zz

  # FIRST STARTS WHERE SECOND ENDS WITHIN k-SLOTS

  def nearAfterR(k):

    def zz(fTp, tTp):
      isSlotF = isSlotType(fTp)
      isSlotT = isSlotType(tTp)
      if isSlotF and isSlotT:
        return lambda n: tuple(m for m in range(max((1, n - 1 - k)), min((maxSlot, n - 1 + k)) + 1))
      else:
        if isSlotT:

          def xx(n):
            myPrev = n - 1 if n < maxSlot else Eoslots[n - maxSlot - 1][0] - 1
            myPrevNear = tuple(
                l for l in range(max((1, myPrev - k)),
                                 min((maxSlot, myPrev + k)) + 1)
            )
            return myPrevNear

        elif isSlotT is None:

          def xx(n):
            myPrev = n - 1 if n < maxSlot else Eoslots[n - maxSlot - 1][0] - 1
            myPrevNear = tuple(
                l for l in range(max((1, myPrev - k)),
                                 min((maxSlot, myPrev + k)) + 1)
            )
            prevSet = set(reduce(
                set.union,
                (set(ClastSlots[l - 1]) for l in myPrevNear),
                set(),
            ))
            return tuple(prevSet) + myPrevNear

        else:

          def xx(n):
            myPrev = n - 1 if n < maxSlot else Eoslots[n - maxSlot - 1][0] - 1
            myPrevNear = tuple(
                l for l in range(max((1, myPrev - k)),
                                 min((maxSlot, myPrev + k)) + 1)
            )
            prevSet = set(reduce(
                set.union,
                (set(ClastSlots[l - 1]) for l in myPrevNear),
                set(),
            ))
            return tuple(prevSet)

        return xx

    return zz

  # EDGES

  def makeEdgeMaps(efName):

    def edgeAccess(eFunc, doValues, value):
      if doValues:
        if value is None:
          return lambda n: tuple(m[0] for m in eFunc(n) if m[1] is None)
        elif value is True:
          return lambda n: tuple(m[0] for m in eFunc(n))
        elif isinstance(value, types.FunctionType):
          return lambda n: tuple(m[0] for m in eFunc(n) if value(m[1]))
        elif isinstance(value, reTp):
          return lambda n: tuple(m[0] for m in eFunc(n) if value is not None and value.search(m[1]))
        else:
          (ident, value) = value
          if (ident is None and value is True):
            return lambda n: tuple(m[0] for m in eFunc(n))
          elif ident:
            return lambda n: tuple(m[0] for m in eFunc(n) if m[1] in value)
          else:
            return lambda n: tuple(m[0] for m in eFunc(n) if m[1] not in value)
      else:
        return lambda n: eFunc(n)

    def edgeRV(value):

      def edgeR(fTp, tTp):
        Es = api.Es
        Edata = Es(efName)
        doValues = Edata.doValues
        return edgeAccess(Edata.f, doValues, value)

      return edgeR

    def edgeIRV(value):

      def edgeIR(fTp, tTp):
        Es = api.Es
        Edata = Es(efName)
        doValues = Edata.doValues
        return edgeAccess(Edata.t, doValues, value)

      return edgeIR

    return (edgeRV, edgeIRV)

  # COLLECT ALL RELATIONS IN A TUPLE

  relations = [
      (
          ('=', spinEqual, equalR, 'left equal to right (as node)'),
          ('=', spinEqual, equalR, None),
      ),
      (
          ('#', 0.999, unequalR, 'left unequal to right (as node)'),
          ('#', 0.999, unequalR, None),
      ),
      (
          ('<', 0.500, canonicalBeforeR, 'left before right (in canonical node ordering)'),
          ('>', 0.500, canonicalAfterR, 'left after right (in canonical node ordering)'),
      ),
      (
          ('==', spinSameSlots, sameSlotsR, 'left occupies same slots as right'),
          ('==', spinSameSlots, sameSlotsR, None),
      ),
      (
          ('&&', spinOverlap, overlapR, 'left has overlapping slots with right'),
          ('&&', spinOverlap, overlapR, None),
      ),
      (
          ('##', 0.990, diffSlotsR, 'left and right do not have the same slot set'),
          ('##', 0.990, diffSlotsR, None),
      ),
      (
          ('||', 0.900, disjointSlotsR, 'left and right do not have common slots'),
          ('||', 0.900, disjointSlotsR, None),
      ),
      (
          ('[[', True, hasR, 'left embeds right'),
          (']]', True, inR, 'left embedded in right'),
      ),
      (
          ('<<', 0.490, slotBeforeR, 'left completely before right'),
          ('>>', 0.490, slotAfterR, 'left completely after right'),
      ),
      (
          ('=:', True, sameFirstSlotR, 'left and right start at the same slot'),
          ('=:', True, sameFirstSlotR, None),
      ),
      (
          (':=', True, sameLastSlotR, 'left and right end at the same slot'),
          (':=', True, sameLastSlotR, None),
      ),
      (
          ('::', True, sameBoundaryR, 'left and right start and end at the same slot'),
          ('::', True, sameBoundaryR, None),
      ),
      (
          ('<:', True, adjBeforeR, 'left immediately before right'),
          (':>', True, adjAfterR, 'left immediately after right'),
      ),
      (
          ('=k:', True, nearFirstSlotR, 'left and right start at k-nearly the same slot'),
          ('=k:', True, nearFirstSlotR, None),
      ),
      (
          (':k=', True, nearLastSlotR, 'left and right end at k-nearly the same slot'),
          (':k=', True, nearLastSlotR, None),
      ),
      (
          (':k:', True, nearBoundaryR, 'left and right start and end at k-near slots'),
          (':k:', True, nearBoundaryR, None),
      ),
      (
          ('<k:', True, nearBeforeR, 'left k-nearly before right'),
          (':k>', True, nearAfterR, 'left k-nearly after right'),
      ),
  ]

  # BUILD AND INITIALIZE ALL RELATIONAL FUNCTIONS

  api.TF.explore(silent=silent)
  edgeMap = {}

  for efName in sorted(api.TF.featureSets['edges']):
    if efName == WARP[1]:
      continue
    r = len(relations)

    (edgeRV, edgeIRV) = makeEdgeMaps(efName)
    doValues = api.TF.features[efName].edgeValues
    extra = ' with value specification allowed' if doValues else ''
    relations.append((
        (f'-{efName}>', True, edgeRV, f'edge feature "{efName}"{extra}'),
        (f'<{efName}-', True, edgeIRV, f'edge feature "{efName}"{extra} (opposite direction)'),
    ))
    edgeMap[2 * r] = (efName, 1)
    edgeMap[2 * r + 1] = (efName, -1)
  lr = len(relations)

  relationsAll = []
  for (r, rc) in relations:
    relationsAll.extend([r, rc])

  searchExe.relations = [dict(
      acro=r[0],
      spin=r[1],
      func=r[2],
      desc=r[3],
  ) for r in relationsAll]
  searchExe.relationFromName = dict(((r['acro'], i) for (i, r) in enumerate(searchExe.relations)))
  searchExe.relationLegend = '\n'.join(
      f'{r["acro"]:>23} {r["desc"]}' for r in searchExe.relations if r['desc'] is not None
  )
  searchExe.relationLegend += f'''
The warp feature "{WARP[1]}" cannot be used in searches.
One of the above relations on nodes and/or slots will suit you better.
'''
  searchExe.converse = dict(
      tuple((2 * i, 2 * i + 1) for i in range(lr)) + tuple((2 * i + 1, 2 * i) for i in range(lr))
  )
  searchExe.edgeMap = edgeMap


def add_K_Relations(searchExe, varRels):
  relations = searchExe.relations
  tasks = collections.defaultdict(set)
  for (acro, ks) in varRels.items():
    j = searchExe.relationFromName[acro]
    ji = searchExe.converse[j]
    if ji < j:
      (j, ji) = (ji, j)
    acro = relations[j]['acro']
    acroi = relations[ji]['acro']
    tasks[(j, acro, ji, acroi)] |= ks

  for ((j, acro, ji, acroi), ks) in tasks.items():
    for k in ks:
      newAcro = acro.replace('k', str(k))
      newAcroi = acroi.replace('k', str(k))
      r = relations[j]
      ri = relations[ji]
      lr = len(relations)
      relations.extend([
          dict(
              acro=newAcro,
              spin=r['spin'],
              func=r['func'](k),
              desc=r['desc'],
          ),
          dict(
              acro=newAcroi,
              spin=ri['spin'],
              func=ri['func'](k),
              desc=ri['desc'],
          ),
      ])
      searchExe.relationFromName[newAcro] = lr
      searchExe.relationFromName[newAcroi] = lr + 1
      searchExe.converse[lr] = lr + 1
      searchExe.converse[lr + 1] = lr


def add_V_Relations(searchExe, varRels):
  relations = searchExe.relations
  tasks = collections.defaultdict(set)
  for (acro, vals) in sorted(varRels.items()):
    for (eName, val) in vals:
      conv = acro[0] == '<'
      eRel = f'-{eName}>'
      eReli = f'<{eName}-'
      acroi = f'-{acro[1:-1]}>' if conv else f'<{acro[1:-1]}-'
      if conv:
        (acro, acroi) = (acroi, acro)
      j = searchExe.relationFromName[eRel]
      ji = searchExe.relationFromName[eReli]
      tasks[(eName, j, acro, ji, acroi)].add(val)

  for ((eName, j, acro, ji, acroi), vals) in sorted(tasks.items()):
    for val in vals:
      r = relations[j]
      ri = relations[ji]
      lr = len(relations)
      relations.extend([
          dict(
              acro=acro,
              spin=r['spin'],
              func=r['func'](val),
              desc=r['desc'],
          ),
          dict(
              acro=acroi,
              spin=ri['spin'],
              func=ri['func'](val),
              desc=ri['desc'],
          ),
      ])
      searchExe.relationFromName[acro] = lr
      searchExe.relationFromName[acroi] = lr + 1
      searchExe.edgeMap[lr] = (eName, 1)
      searchExe.edgeMap[lr + 1] = (eName, -1)
      searchExe.converse[lr] = lr + 1
      searchExe.converse[lr + 1] = lr
