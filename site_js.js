(function(){
  // rates in CLP as [low, high]
  var RATES = {
    trailer:       [500000, 500000],
    recommission:  [80000, 180000],     // bearings, tyres, lights, paint on a used trailer
    frame:         [5000, 8000],        // per m2 of (wall+ceil+floor) — pino radiata studs/plates
    subfloor:      [9000, 14000],       // per m2 floor — OSB + treated deck + anchor bolts
    insul: { glasswool:[2200,3200], mineralwool:[4200,5500] }, // per m2 (wall+ceil)
    vapor:         [1500, 2500],        // per m2 lining — foil + tape
    ext:   { impregnado:[7000,11000], fibrocemento:[9000,14000] }, // per m2 wall
    lining:{ alamo:[12000,20000], nativo:[18000,30000] },          // per m2 lining
    bench: { alamo:[9000,15000],  nativo:[14000,24000] },          // per linear m
    heater:{ electric45:[220000,320000], woodBuena:[504000,660000], woodNordica:[1290000,1290000] },
    install:[120000,220000],            // electric only: SEC electrician + breaker/RCD + cable
    flue:          [386000, 435000],    // wood (Buena) only; Nordica includes
    stones:        [16000, 32000],      // electric & woodBuena; Nordica includes
    door:  { solid:[60000,110000], glass:[150000,260000] },
    vent:          [20000, 45000],
    lighting:      [25000, 60000],
    fixtures:      [30000, 70000],      // thermo/hygro, bucket, ladle, duckboard
    misc:          [60000, 110000]      // fasteners, sealant, sundries
  };
  // weight kg
  var WT = {
    perWallCeil: 16, perFloor: 28, benchPerM: 9,
    door: { solid:25, glass:35 },
    heater: { electric45:20, woodBuena:65, woodNordica:95 },
    stones: { electric45:25, woodBuena:25, woodNordica:30 },
    fixed: 30
  };
  var PRESETS = {
    lean:        { heater:'electric45', insul:'glasswool',   wood:'alamo',  ext:'impregnado',   door:'solid' },
    comfortable: { heater:'woodBuena',  insul:'mineralwool', wood:'alamo',  ext:'impregnado',   door:'glass' },
    premium:     { heater:'woodNordica',insul:'mineralwool', wood:'nativo', ext:'fibrocemento', door:'glass' }
  };

  function $(id){ return document.getElementById(id); }
  function clp(n){ return '$' + Math.round(n).toLocaleString('es-CL'); }
  function add(a,b){ return [a[0]+b[0], a[1]+b[1]]; }
  function scale(r,f){ return [r[0]*f, r[1]*f]; }

  function compute(){
    var W=+$('w').value||1.7, L=+$('l').value||3.0, H=+$('h').value||2.0;
    var heater=$('heater').value, insul=$('insul').value, wood=$('wood').value,
        ext=$('ext').value, door=$('door').value, inc=$('incTrailer').checked;

    var floor=W*L, ceil=W*L, wall=2*(W+L)*H, lining=wall+ceil, benchLen=2*L;
    var vol=W*L*H, usable=vol*0.8;
    var kW=Math.min(12, Math.max(4.5, Math.round(usable)));

    var items=[];
    function push(label, r){ if(r[1]>0) items.push([label, r]); }

    if(inc) push('Second-hand trailer', RATES.trailer);
    push('Trailer recommission (bearings, tyres, lights)', RATES.recommission);
    push('Frame — pino radiata', scale(RATES.frame, wall+ceil+floor));
    push('Subfloor, deck & chassis anchoring', scale(RATES.subfloor, floor));
    push('Insulation — '+(insul==='glasswool'?'glass wool':'mineral wool'), scale(RATES.insul[insul], wall+ceil));
    push('Vapor barrier (foil + tape)', scale(RATES.vapor, lining));
    push('Exterior skin — '+(ext==='impregnado'?'pino impregnado':'fibrocemento'), scale(RATES.ext[ext], wall));
    push('Interior lining — '+(wood==='alamo'?'álamo':'native wood'), scale(RATES.lining[wood], lining));
    push('Benches — '+(wood==='alamo'?'álamo':'native wood'), scale(RATES.bench[wood], benchLen));
    // heater group
    var hlabel = heater==='electric45' ? 'Electric heater 4.5 kW'
               : heater==='woodBuena'  ? 'Wood stove (BuenaCaldera)'
               : 'Wood stove (Nordicasa, premium)';
    push(hlabel, RATES.heater[heater]);
    if(heater==='electric45') push('Electric install (SEC electrician + breaker + cable)', RATES.install);
    if(heater==='woodBuena')  push('Double-wall flue kit', RATES.flue);
    if(heater!=='woodNordica') push('Volcanic sauna stones', RATES.stones);
    push('Door — '+(door==='glass'?'tempered glass':'solid wood'), RATES.door[door]);
    push('Ventilation (vents + fresh-air intake)', RATES.vent);
    push('Lighting (heat-rated / LED)', RATES.lighting);
    push('Fixtures (thermo/hygro, bucket, ladle, duckboard)', RATES.fixtures);
    push('Fasteners, sealant & sundries', RATES.misc);

    var total=[0,0]; items.forEach(function(it){ total=add(total,it[1]); });

    // weight (empty, towing)
    var wkg = WT.perWallCeil*(wall+ceil) + WT.perFloor*floor + WT.benchPerM*benchLen
            + WT.door[door] + WT.heater[heater] + WT.stones[heater] + WT.fixed;

    // render badges
    $('badges').innerHTML =
      badge(vol.toFixed(1)+' m³','cabin volume') +
      badge(usable.toFixed(1)+' m³','usable (hot room)') +
      badge('~'+kW+' kW','recommended heater') +
      badge('~'+Math.round(wkg)+' kg','built weight (towing)');

    // weight bar + warning
    var pct=Math.min(100, wkg/1500*100);
    $('wfill').style.width=pct.toFixed(0)+'%';
    var ww=$('wwarn');
    if(wkg<=600){ ww.className='warn ok'; ww.textContent='✅ Comfortable on a 750 kg single axle — good margin for stove, water and bathers.'; }
    else if(wkg<=750){ ww.className='warn ok'; ww.textContent='⚠️ Fits a 750 kg axle but with little margin once you add water and 2–3 people. Prefer a 1000 kg+ axle.'; }
    else if(wkg<=1100){ ww.className='warn bad'; ww.textContent='⛔ Too heavy for a 750 kg axle. You need a trailer rated ~1000–1200 kg+ (PBT). Verify the axle plate before buying.'; }
    else { ww.className='warn bad'; ww.textContent='⛔ Heavy build (~'+Math.round(wkg)+' kg). Requires a 1500 kg+ axle and brakes (>750 kg capacity is legally required to have brakes in Chile). Consider shrinking the cabin.'; }

    // table
    var rows='';
    items.forEach(function(it){
      rows+='<tr><td class="ci">'+it[0]+'</td><td class="cp">'+clp(it[1][0])+' – '+clp(it[1][1])+'</td></tr>';
    });
    $('calc-table').innerHTML=rows;
    $('grand').textContent=clp(total[0])+' – '+clp(total[1]);
  }
  function badge(v,l){ return '<div class="badge"><div class="v">'+v+'</div><div class="l">'+l+'</div></div>'; }

  function applyPreset(name){
    var p=PRESETS[name]; if(!p) return;
    $('heater').value=p.heater; $('insul').value=p.insul; $('wood').value=p.wood;
    $('ext').value=p.ext; $('door').value=p.door;
    Array.prototype.forEach.call(document.querySelectorAll('.preset'),function(b){
      b.classList.toggle('active', b.getAttribute('data-preset')===name);
    });
    compute();
  }

  document.addEventListener('DOMContentLoaded', function(){
    ['w','l','h','heater','insul','wood','ext','door','incTrailer'].forEach(function(id){
      var el=$(id); if(el){ el.addEventListener('input',compute); el.addEventListener('change',compute); }
    });
    Array.prototype.forEach.call(document.querySelectorAll('.preset'),function(b){
      b.addEventListener('click',function(){ applyPreset(b.getAttribute('data-preset')); });
    });
    compute();
  });
})();
