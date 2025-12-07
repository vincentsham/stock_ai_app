export const DISCLAIMER_TEXT = `This is for informational purposes only, not financial advice. 
      Be aware: The AI system may occasionally generate incorrect or incomplete information. 
      Invest responsibly and conduct your own due diligence.`;


export const EARNINGS_TAG_METADATA: Record<string, { label: string; description: string; className: string }> = {
      'consistent-outperform': {
            label: 'Consistent Outperform',
            description: 'Recorded Wall Street estimate beats in >=3 consecutive quarters.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      },    
      'frequent-beat': {
            label: 'Frequent Beat',
            description: 'Recorded Wall Street estimate beats in 3 of the last 4 quarters.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      },  
      'broken-beat-streak': {
            label: 'Broken Beat Streak',
            description: 'Recorded Wall Street estimate beats in 3 of the last 4 quarters but missed the latest result.',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },    
      'emerging-beat': {
            label: 'Emerging Beat',
            description: 'Recorded Wall Street estimate beats in the last 2 quarters after earlier misses.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      },
      'mixed-performance': {
            label: 'Mixed Performance',
            description: 'Recorded Wall Street estimate beats in 2 of the last 4 quarters without a recent streak.',
            // className: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'consistent-miss': {
            label: 'Consistent Miss',
            description: 'Recorded Wall Street estimate misses in >=3 of the last 4 quarters.',
            className: 'bg-[#ef4444]/10 text-[#ef4444] border-[#ef4444]/20',
      },
      'sustained-expansion': {
            label: 'Sustained Expansion',
            description: 'Recorded positive YoY growth in >=3 consecutive quarters.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      },    
      'developing-expansion': {
            label: 'Developing Expansion',
            description: 'Recorded positive YoY growth in 3 of the last 4 quarters.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      },   
      'broken-growth-streak': {
            label: 'Broken Expansion Streak',
            description: 'Recorded positive YoY growth in 3 of the last 4 quarters but contracted most recently.',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },   
      'emerging-growth': {
            label: 'Emerging Growth',
            description: 'Recorded positive YoY growth in the last 2 quarters after earlier contraction.',
            // className: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'volatile-growth': {
            label: 'Volatile Growth',
            description: 'Recorded positive YoY growth in 2 of the last 4 quarters without a recent streak.',
            // className: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'tentative-turnaround': {
            label: 'Tentative Turnaround',
            description: 'Recorded positive YoY growth after >=3 consecutive contraction quarters.',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'persistent-contraction': {
            label: 'Persistent Contraction',
            description: 'Recorded negative YoY growth in >=3 of the last 4 quarters.',
            className: 'bg-[#ef4444]/10 text-[#ef4444] border-[#ef4444]/20',
      },
      'sustained-acceleration': {
            label: 'Sustained Acceleration',
            description: 'Recorded YoY growth-rate acceleration in 3 of the last 4 quarters including a recent >=2-quarter streak.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      }, 
      'choppy-acceleration': {
            label: 'Choppy Acceleration',
            description: 'Recorded YoY growth-rate acceleration in 3 of the last 4 quarters.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      }, 
      'broken-acceleration-streak': {
            label: 'Broken Acceleration Streak',
            description: 'Recorded YoY growth-rate acceleration in 3 of the last 4 quarters but slowed most recently.',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'emerging-acceleration': {
            label: 'Emerging Acceleration',
            description: 'Recorded YoY growth-rate acceleration in the last 2 quarters after earlier stagnation.',
            className: 'bg-[#22c55e]/10 text-[#22c55e] border-[#22c55e]/20',
      },
      'unstable-momentum': {
            label: 'Unstable Momentum',
            description: 'Recorded YoY growth-rate acceleration in 2 of the last 4 quarters without a recent streak.',
            // className: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'broken-deceleration-streak': {
            label: 'Broken Deceleration Streak',
            description: 'Recorded YoY growth-rate deceleration in 3 of the last 4 quarters but re-accelerated most recently.',
            className: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      },
      'persistent-deceleration': {
            label: 'Persistent Deceleration',
            description: 'Recorded YoY growth-rate deceleration in >=3 of the last 4 quarters.',
            className: 'bg-[#ef4444]/10 text-[#ef4444] border-[#ef4444]/20',
      },
      'unknown': {
            label: 'Unknown',
            description: 'Insufficient data to classify the trend.',
            className: 'hidden bg-purple-500/10 text-purple-400 border-purple-500/20',
      },
};