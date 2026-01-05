import Header from "@/components/Header"
import Footer from "@/components/Footer"

const Layout = async ({ children }: { children : React.ReactNode }) => {

    return (
        <main className="min-h-screen flex flex-col text-gray-400">
            <div className="relative z-50">
                <Header  />
            </div>
            <div className="container py-10 flex-grow">
                {children}
            </div>
            <div className="relative z-50">
                <Footer />
            </div>
            
        </main>
    )
}
export default Layout

// import Header from "@/components/Header"
// import Footer from "@/components/Footer"

// const Layout = async ({ children }: { children : React.ReactNode }) => {

//     return (
//         // Added 'relative' to main to ensure it establishes a positioning context if needed
//         <main className="min-h-screen flex flex-col text-gray-400 relative">
//             <Header />
            
//             {/* FIXED: Removed "container py-10" class. 
//                Changed to "w-full flex-grow" so it allows full-width backgrounds (like the wallpaper).
               
//                NOTE: Individual pages that need centering (like stock details) should now 
//                add 'container mx-auto py-10' to their own wrapper div.
//             */}
//             <div className="flex-grow w-full">
//                 {children}
//             </div>
            
//             <Footer />
//         </main>
//     )
// }
// export default Layout