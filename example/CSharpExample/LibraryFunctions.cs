using System;
using System.Text;

namespace CSharpExample
{
    public static class LibraryFunctions
    {
        public static int PrintHelloWorld(IntPtr argPtr, int argSize)
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.WriteLine($"Hello world! 世界に挨拶します　argPtr={argPtr} argSize={argSize}");
            return 0;
        }
    }
}
