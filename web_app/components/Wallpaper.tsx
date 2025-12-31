"use client";

import { useEffect, useState } from "react";

// ----------------------------------------------------------------------
// 1. CONFIGURATION
// ----------------------------------------------------------------------
const SCREENSHOTS = [
    "/assets/wallpapers/wallpaper0.png", 
    "/assets/wallpapers/wallpaper1.png", 
    "/assets/wallpapers/wallpaper2.png",
    "/assets/wallpapers/wallpaper3.png",
    "/assets/wallpapers/wallpaper4.png", 
    "/assets/wallpapers/wallpaper5.png",
    "/assets/wallpapers/wallpaper6.png",
    "/assets/wallpapers/wallpaper7.png", 
];

// Duplicate the array to ensure we have enough items to fill the scrolling columns
const GRID_ITEMS = [...SCREENSHOTS, ...SCREENSHOTS, ...SCREENSHOTS];

export const Wallpaper = () => {
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) return null;

    return (
        <div className="fixed inset-0 h-screen w-screen overflow-hidden bg-[#0a0a0a] z-0 pointer-events-none">
            
            {/* SCALING ADJUSTMENT:
               Since we made the cards wider, we might need to adjust the gap or scale slightly 
               to fit them nicely.
            */}
            <div className="absolute left-1/2 top-1/2 h-[200vh] w-[200vw] -translate-x-1/2 -translate-y-1/2 -rotate-12 scale-125 opacity-[0.7]">
                
                <div className="flex w-full items-center justify-center gap-8"> 
                    {/* Increased gap from 6 to 8 for breathing room */}

                    {/* Column 1 */}
                    <div className="flex flex-col gap-8 animate-scroll-up will-change-transform">
                        {GRID_ITEMS.map((src, i) => (
                           <Card key={`c1-${i}`} src={src} />
                        ))}
                    </div>

                    {/* Column 2 */}
                    <div className="flex flex-col gap-8 animate-scroll-down will-change-transform">
                        {GRID_ITEMS.map((src, i) => (
                           <Card key={`c2-${i}`} src={src} />
                        ))}
                    </div>

                    {/* Column 3 */}
                    <div className="flex flex-col gap-8 animate-scroll-up will-change-transform">
                        {GRID_ITEMS.map((src, i) => (
                           <Card key={`c3-${i}`} src={src} />
                        ))}
                    </div>
                </div>
            </div>

            {/* THE GRADIENT OVERLAY (Vignette) */}
            <div className="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-transparent to-[#0a0a0a]" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_transparent_0%,_#0a0a0a_100%)]" />

            {/* CSS Animations */}
            <style jsx global>{`
                @keyframes scroll-up {
                    0% { transform: translateY(0); }
                    100% { transform: translateY(-33.33%); } 
                }
                @keyframes scroll-down {
                    0% { transform: translateY(-33.33%); }
                    100% { transform: translateY(0); }
                }
                .animate-scroll-up {
                    animation: scroll-up 60s linear infinite;
                }
                .animate-scroll-down {
                    animation: scroll-down 60s linear infinite;
                }
                .will-change-transform {
                    will-change: transform;
                }
            `}</style>
        </div>
    );
};

// Helper Card Component
const Card = ({ src }: { src: string }) => {
    const [error, setError] = useState(false);

    return (
        // CHANGED DIMENSIONS FOR DESKTOP SCREENSHOTS:
        // Width: 320px (Wider)
        // Height: 180px (Shorter)
        // Aspect Ratio: 16:9
        // REMOVED 'border' classes to match request
        <div className={`relative h-[180px] w-[320px] flex-shrink-0 overflow-hidden rounded-xl shadow-2xl backdrop-blur-sm transition-colors duration-500
            ${error ? 'bg-gray-800/50' : 'bg-gray-800'}`}>
             
             {error ? (
                 <div className="flex h-full w-full items-center justify-center p-4 text-center">
                     <div className="h-10 w-10 rounded-full bg-white/5" />
                 </div>
             ) : (
                 <>
                     {/* Vignette Overlay: Adds an inset shadow to "blur" the hard edges into the card */}
                     <div className="absolute inset-0 z-10 shadow-[inset_0_0_40px_10px_rgba(0,0,0,0.6)] pointer-events-none rounded-xl" />
                     
                     {/* eslint-disable-next-line @next/next/no-img-element */}
                     <img 
                       src={src} 
                       alt="App Screenshot" 
                       // object-cover still ensures it fills the box, but now the box matches the shape of a monitor
                       className="h-full w-full object-cover" 
                       onError={() => setError(true)}
                     />
                 </>
             )}
        </div>
    )
}