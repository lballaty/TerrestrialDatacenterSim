// ==========================================================================
// SHARED COMPUTE CATALOG — identical in OrbitalDatacenterSim and TerrestrialDatacenterSim
// Source of truth: keep these three blocks (STACKS, MODELS, throughput helpers)
// byte-identical across both tools except for the terrestrial-only STACKS rows,
// which are flagged terrestrialOnly:true and never launched to orbit.
// Catalog version: 3.0.0 (2026-09-05)
// ==========================================================================
const STACKS={
  gb300:{name:'NVIDIA GB300 NVL72',rkw:135,rpk:155,rm:1580,gpu:72,rcost:4,nodes:18,memtype:'hbm',stackrad:1.25,procurable:'yes',
    tps:{small:20e6,mid:6e6,large:2.8e6},src:{small:'estimate',mid:'estimate',large:'measured'},
    note:'Rack TDP and mass from Lenovo GB300 NVL72. Large-MoE cell: 2.8M tok/s/MW at 116 tok/s/user (SemiAnalysis InferenceX, cited by NVIDIA, 2026). Small/mid cells scale by active-parameter ratio and are estimates.'},
  rubin:{name:'NVIDIA Vera Rubin NVL72',rkw:190,rpk:220,rm:1700,gpu:72,rcost:5.5,nodes:18,memtype:'hbm',stackrad:1.25,procurable:'limited',
    tps:{small:40e6,mid:12e6,large:5.5e6},src:{small:'estimate',mid:'estimate',large:'estimate'},
    note:'SemiAnalysis (July 2026) puts Rubin near 2× GB300 throughput at ≤100 tok/s/user. Rack power, mass and price are estimates; allocation is constrained through 2027.'},
  mi455x:{name:'AMD Helios MI455X',rkw:200,rpk:230,rm:1700,gpu:72,rcost:5.25,nodes:18,memtype:'hbm',stackrad:1.25,procurable:'yes',
    tps:{small:40e6,mid:12e6,large:5.5e6},src:{small:'estimate',mid:'estimate',large:'estimate'},
    note:'72 MI455X, 31 TB HBM4, 2.9 EF FP4 (AMD, July 2026). Rack price ~$5.25M reported by Tech Insider. AMD claims +30% tokens/$ vs Rubin on Kimi K2 Thinking (vendor benchmark). Rack power is an estimate; InferenceX results pending.'},
  tpu7:{name:'Google Ironwood TPU v7',rkw:75,rpk:90,rm:1000,gpu:64,rcost:2.5,nodes:16,memtype:'hbm',stackrad:1.1,procurable:'no',
    tps:{small:22e6,mid:6.5e6,large:3e6},src:{small:'estimate',mid:'estimate',large:'estimate'},
    note:'~1 kW/chip inferred from 9,216-chip pod at ~10 MW (HPCwire). Not merchant hardware: a third-party operator cannot buy it. Google claims 44% lower TCO than GB200 in pod configuration. Radiation multiplier lower only because Google has published proton data for the prior generation.'},
  groq3:{name:'NVIDIA Groq 3 LPX',rkw:120,rpk:140,rm:1400,gpu:256,rcost:3,nodes:32,memtype:'sram',stackrad:1.6,procurable:'limited',
    tps:{small:30e6,mid:null,large:null},src:{small:'estimate',mid:'n/a',large:'n/a'},
    note:'256 LPUs in 32 trays, 128 GB total on-die SRAM, 40 PB/s (NVIDIA developer blog). Headline 3,400 tok/s is single-stream on a 31B model; concurrency at 100K context caps near batch 12. 128 GB cannot hold trillion-parameter weights, so mid/large cells are not servable without a Rubin prefill/attention partner. Power, mass and price are estimates.'},
  cs4:{name:'Cerebras CS-4',rkw:75,rpk:90,rm:1200,gpu:3,rcost:7,nodes:3,memtype:'wafer',stackrad:2,procurable:'limited',
    tps:{small:25e6,mid:5e6,large:1.5e6},src:{small:'estimate',mid:'estimate',large:'estimate'},
    note:'Three WSE-3 Turbo wafers (44 GB SRAM each) on the Nexus platform, announced August 2026. Large models rely on external weight memory. Full-wafer die area drives the highest SEE cross-section of any stack. All figures are estimates.'},
  trn3:{name:'AWS Trainium3 rack',rkw:120,rpk:140,rm:1400,gpu:64,rcost:3,nodes:16,memtype:'hbm',stackrad:1.25,procurable:'no',
    tps:{small:18e6,mid:5e6,large:2.2e6},src:{small:'estimate',mid:'estimate',large:'estimate'},
    note:'Captive to AWS; included for comparison only. All figures are estimates.'}
,
  // --- terrestrial-only stacks (land / sea / undersea; not launchable) ---
  mi355x:{name:'AMD MI355X server (8-GPU)',rkw:12,rpk:14,rm:0,gpu:8,rcost:0.30,nodes:1,memtype:'hbm',procurable:'yes',terrestrialOnly:true,
    tps:{small:36e6,mid:11e6,large:5e6},src:{small:'estimate',mid:'estimate',large:'estimate'},
    note:'Merchant 8-GPU server, air/DLC. Server-granularity swap. Terrestrial-only. Figures estimates.'},
  b300srv:{name:'NVIDIA B300 HGX server (8-GPU)',rkw:14,rpk:16,rm:0,gpu:8,rcost:0.42,nodes:1,memtype:'hbm',procurable:'yes',terrestrialOnly:true,
    tps:{small:20e6,mid:6e6,large:2.8e6},src:{small:'estimate',mid:'estimate',large:'measured'},
    note:'Merchant 8-GPU Blackwell Ultra server; per-GPU throughput mirrors GB300. Terrestrial-only server granularity.'},
  gaudi3:{name:'Intel Gaudi 3 server',rkw:8,rpk:9,rm:0,gpu:8,rcost:0.16,nodes:1,memtype:'hbm',procurable:'yes',terrestrialOnly:true,
    tps:{small:12e6,mid:3.5e6,large:1.4e6},src:{small:'estimate',mid:'estimate',large:'estimate'},
    note:'Air-coolable, lowest $/accelerator. Terrestrial-only. Figures estimates.'},
  ascend:{name:'Huawei Ascend 910C / CloudMatrix',rkw:145,rpk:170,rm:0,gpu:384,rcost:3.2,nodes:48,memtype:'hbm',procurable:'region-restricted',terrestrialOnly:true,
    tps:{small:16e6,mid:5e6,large:2.4e6},src:{small:'estimate',mid:'estimate',large:'estimate'},
    note:'Region-restricted (China). Immersion-friendly for sea/undersea siting. Figures estimates.'}
};

const MODELS={
  dsv4pro:{name:'DeepSeek V4 Pro',mclass:'large',mparams:1600,mactive:49,fp:{i:.435,o:.87},nh:{i:2.1,o:4.4},mlic:0,latclass:'agentic',
    note:'First-party API $0.435/$0.87 per 1M (BenchLM, July 2026); neutral hosts charge $2.10/$4.40 (Together). Open weights, no licence cost. DeepSeek has signalled a price increase without a date.'},
  dsv4flash:{name:'DeepSeek V4 Flash',mclass:'mid',mparams:300,mactive:20,fp:{i:.14,o:.28},nh:null,mlic:0,latclass:'agentic',
    note:'First-party $0.14/$0.28 per 1M. Parameter counts are placeholders; size class is the load-bearing input.'},
  kimik26:{name:'Kimi K2.6',mclass:'large',mparams:1000,mactive:32,fp:null,nh:{i:1.2,o:4.5},mlic:0,latclass:'agentic',
    note:'Together AI $1.20/$4.50 per 1M. Open weights under a custom licence with commercial conditions: verify before assuming zero licence cost.'},
  glm52:{name:'GLM-5.2',mclass:'large',mparams:744,mactive:40,fp:{i:1.4,o:4.4},nh:{i:1.4,o:4.4},mlic:0,latclass:'agentic',
    note:'$1.40/$4.40 per 1M (z.ai / Together). MIT-licensed weights.'},
  gptoss120:{name:'gpt-oss 120B',mclass:'small',mparams:120,mactive:5,fp:null,nh:{i:.15,o:.6},mlic:0,latclass:'interactive',
    note:'Together AI $0.15/$0.60 per 1M. Apache-2.0 weights. High tokens/MW, so the relay link becomes the binding constraint.'},
  llama70:{name:'Llama 3.3 70B',mclass:'small',mparams:70,mactive:70,fp:null,nh:{i:.88,o:.88},mlic:0,latclass:'interactive',
    note:'Together AI $0.88 flat per 1M. Dense model: active = total parameters.'},
  frontier:{name:'Frontier proprietary (licensed)',mclass:'large',mparams:2000,mactive:100,fp:{i:2,o:12},nh:{i:2,o:12},mlic:4,latclass:'agentic',
    note:'Scenario: a third-party operator serving a frontier model under a per-token licence. Price tier and $4/1M licence are illustrative; no vendor publishes such terms.'}
}

// Shared throughput selection: stack × model-class → tokens/s/MW, with an optional
// interactivity factor (tpsuRef/tpsu)^interAlpha, identical to the orbital tool.
function stackTps(stackId, mclass){ const st=STACKS[stackId]; if(!st) return null; const v=st.tps[mclass]; return (v===null||v===undefined)?null:v; }
function interactivityFactor(on, tpsuRef, tpsu, alpha){ return on? Math.max(.2, Math.min(3, Math.pow(Math.max(1,tpsuRef)/Math.max(1,tpsu), alpha))) : 1; }
function effectiveTpsMW(stackId, mclass, opts){ const base=stackTps(stackId,mclass); if(base===null) return null; const o=opts||{}; return base*interactivityFactor(!!o.interOn, o.tpsuRef||116, o.tpsu||116, (o.alpha==null?0.9:o.alpha)); }
// blended market price $/1M tokens from a model's fp/nh input/output tiers (3:1 output-weighted, first-party if present else neutral host)
function modelBlendedPrice(m){ if(!m) return null; const t=m.fp||m.nh; if(!t) return null; return (t.i+3*t.o)/4; }
