const { Kafka, Admin } = require('kafkajs');

// Define Kafka broker(s)
const kafka = new Kafka({
  brokers: ['34.133.89.239:9092'],
});

// Create Kafka admin client
const admin = kafka.admin();

// Create Kafka producer
const producer = kafka.producer();

// Create Kafka consumer for requests
const requestConsumer = kafka.consumer({ groupId: 'request-consumer-group' });

// Create Kafka consumer for results
const resultConsumer = kafka.consumer({ groupId: 'result-consumer-group' });

// Define topics
const requestTopic = 'authentication-requests';
const resultTopic = 'authentication-results';

// Create a keyed topic for results
async function createKeyedTopic() {
  try {
    await admin.connect();
    await admin.createTopics({
      topics: [
        {
          topic: resultTopic,
          numPartitions: 1,  // Set the number of partitions as needed
          replicationFactor: 1,
          configEntries: [
            { name: 'cleanup.policy', value: 'compact' },
          ],
        },
      ],
    });
  } catch (error) {
    console.error('Error creating topic:', error);
  } finally {
    await admin.disconnect();
  }
}

// Producer submitting request
async function submitRequest(requestID, requestMessage) {
try {
    await producer.connect();
    await producer.send({
      topic: requestTopic,
      messages: [
        { key: requestID, value: requestMessage },
      ],
    });
    console.log(`Message ID = ${requestID} sent !!!`);
    await producer.disconnect();
} catch (error) {
  console.log(`Error occured: ${error}`);
}
}

// Consumer processing request and publishing result
async function processRequestAndPublishResult() {
  try {
    await requestConsumer.connect(); console.log(`Consumer connected!!!`);
    await requestConsumer.subscribe({ topic: requestTopic }); console.log(`Subcribed to topic: ${requestTopic}`);
  
    await requestConsumer.run({
      eachMessage: async ({ message }) => {
        const requestID = message.key.toString();
        const requestMessage = message.value.toString();
        console.log(`MessageID: ${requestID} received!!!`);
  
        // Process the request and generate the result
        //const resultMessage = `${requestMessage}@Processed`;
        const resultStatus = requestMessage.toString().includes("pass") ? "True" : "False";
  
        // Publish the result to the keyed topic
        await producer.connect();
        await producer.send({
          topic: resultTopic,
          messages: [
            { key: requestID, value: resultStatus },
          ],
        });
        console.log(`Result ${requestID} published!!!`)
        await producer.disconnect();
      },
    });
  } catch (error) {
    console.log(`Error occured: ${error}`);
  }
}

// Producer retrieving result
async function retrieveResult(requestID) {
  await resultConsumer.connect(); console.log(`Consummer connected!`);
  await resultConsumer.subscribe({ topic: resultTopic, fromBeginning: true }); console.log(`Subcribed to Topic ${resultTopic}`)

  let resultFound = false;

  while (!resultFound) {
    const messages = await resultConsumer.run({
      eachMessage: async ({ message, partition, offset }) => {
        const resultID = message.key.toString();
        const resultMessage = message.value.toString();
        console.log(`Message = ${resultID}=${requestID} | ${resultMessage}`);
        console.log(`Partition = ${partition.toString()}`);
        console.log(`resultFound = ${resultFound}`);

        //await new Promise(resolve => setTimeout(resolve, 2000));
        //console.log(`Offset = ${offset.toString()}`);

        // Check if the result matches the desired request ID
        if (resultID === requestID) {
          console.log(`Received result for ${resultID}: ${resultMessage}`);
          resultFound = true;
          // Commit the offset to stop further processing
          await resultConsumer.commitOffsets([{ topic: resultTopic, partition, offset }]);
        }
      },
    });

    if (!resultFound) {
      console.log(`Result for ${requestID} not found at this time. Retrying...`);
      // Wait for a moment before the next polling attempt
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

// Usage
(async () => {
  // Create keyed topic (run this only once)
  await createKeyedTopic();

  // Submit a request
  const requestID = 'ade@gmail.com';
  const requestMessage = 'Password';

  /*  for (let i = 1; i <= 20; i++) {    
    await submitRequest(`ade4sure${i}@gmail.com`, `${requestMessage}`);
  }   
 */
  // Simulate processing and publishing of result
  await processRequestAndPublishResult();

  // Retrieve the result for the specific request ID continuously
  //await retrieveResult(requestID);

})();
