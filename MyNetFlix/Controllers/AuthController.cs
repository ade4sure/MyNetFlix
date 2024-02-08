using Confluent.Kafka;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using MyNetFlix.Models;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace MyNetFlix.Controllers
{
    public class AuthController : Controller
    {

        // GET: Auth/Create
        public ActionResult Login()
        {
            return View();
        }

        // POST: Auth/Create
        [HttpPost]
        [ValidateAntiForgeryToken]
        public async Task<ActionResult> Login(User AppUser)
        {
            //Send User credential to Kafka
            var requestTopic = "authentication-requests";
            var resultTopic = "authentication-results";
            var bootstrapServers = "10.128.0.6:9092";

            var resultConsumerConfig = new ConsumerConfig
            {
                GroupId = "result-consumer-group",
                BootstrapServers = bootstrapServers,
                AutoOffsetReset = AutoOffsetReset.Earliest
            };

            //var requestId = AppUser.Email;
            var requestId = new Guid().ToString();
            var requestMessage = $"{AppUser.Email} | {AppUser.Password}";
            var resultMessage = "False";

            
            var producerConfig = new ProducerConfig { BootstrapServers = bootstrapServers };

            using (var producer = new ProducerBuilder<string, string>(producerConfig).Build())
            {
                var message = new Message<string, string>
                {
                    Key = requestId,
                    Value = requestMessage
                };
                await producer.ProduceAsync(requestTopic, message);
                Console.WriteLine("Message sent succesfully");
            };

            //Fetch response from kafka
            using (var resultConsumer = new ConsumerBuilder<string, string>(resultConsumerConfig).Build())
            {

                resultConsumer.Subscribe(resultTopic);
                //await RetrieveResult(resultConsumer, requestId, resultTopic);

                await Task.Run(async () =>
                {
                    while (true)
                    {
                        var consumeResult = resultConsumer.Consume(TimeSpan.FromSeconds(1));
                        if (consumeResult != null)
                        {
                            var resultId = consumeResult.Message.Key;
                            

                            // Check if the result matches the desired request ID
                            if (resultId == requestId)
                            {
                                resultMessage = consumeResult.Message.Value;
                                Console.WriteLine($"Received result for {resultId}: {resultMessage}");
                                break;
                            }
                        }
                    }
                });
            };

            return resultMessage == "False" ? View() : RedirectToAction("UserHome", "Home");
        }
    }
}
