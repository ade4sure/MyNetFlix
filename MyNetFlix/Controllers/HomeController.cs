using Microsoft.AspNetCore.Mvc;
using MyNetFlix.Models;
using System.Diagnostics;
using System.Drawing;

namespace MyNetFlix.Controllers
{
    public class HomeController : Controller
    {
        private readonly ILogger<HomeController> _logger;

        public HomeController(ILogger<HomeController> logger)
        {
            _logger = logger;
        }

        public IActionResult Index()
        {
            return View();
        }

        public IActionResult UserHome(string category)
        {
            // Create a list of pets.
            List<Movie> MoviesList =
            new List<Movie>{ new Movie { Title = "Maami", Category = "Yoruba Movies", Filename="maami.mp4", Producer = "Funke Akindele", Year = 2017 },
                       new Movie { Title = "Knuckles", Category = "Cartoon", Filename="knuckle.mp4", Producer = "Paramount Plus", Year = 2022 },
                       new Movie { Title = "Lal Salaam", Category = "Indian Movies", Filename="salaam.mp4", Producer = "Various", Year = 2020 },
                       new Movie { Title = "Moana", Category = "Cartoon", Filename="moana.mp4", Producer = "Disney Plus", Year = 2024 },
                       new Movie { Title = "Ayinla Omo Wura", Category = "Yoruba Movies", Filename="ayinla.mp4", Producer = "Ayinla", Year = 2018 },
                       new Movie { Title = "Kangun Kangun", Category = "Mainframe Movies", Filename="kangun.mp4", Producer = "Tunde Kilani", Year = 2016 },
                       new Movie { Title = "Saworo Ide (Brass Bell)", Category = "Mainframe Movies", Filename="saworo.mp4", Producer = "Tunde Kilani", Year = 2020 },
                       };

            var retModel = new MoviesDTO();
            var userMovies = new List<Movie>();
            if (category != null)
            {
                userMovies = MoviesList.Where(m => m.Category == category).ToList();
            }

            retModel.Movies = userMovies;
            retModel.Categories = MoviesList.OrderBy(o => o.Category)
                                            .GroupBy(mov => mov.Category)
                                            .Select(g => g.Key)
                                            .ToList();


            return View(retModel);
        }

        public IActionResult Privacy()
        {
            return View();
        }

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
